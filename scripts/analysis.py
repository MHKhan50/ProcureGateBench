"""Analyse finished ProcureGateBench runs.

Reads outputs/{rule,flat,risk-only}/per_case.csv and every outputs/llm/<config>/per_case.csv,
recomputes the metrics with the package's own scorer, and adds cluster-bootstrap intervals that
resample the 16 hard-gate groups (pair_id), so the six matched cases of a group stay together.

Writes results/results.json, results/tables.md and, if matplotlib is installed, two charts.
"""
import argparse
import ast
import csv
import json
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from procuregatebench.metrics import compute_metrics  # noqa: E402
from procuregatebench.runner import load_records  # noqa: E402

BASELINES = ["rule", "flat", "risk-only"]
PROFILES = ["single_bidder", "short_tender_period", "repeat_awards", "restrictive_specification", "compound"]
PROFILE_LABELS = {"single_bidder": "Single bidder", "short_tender_period": "Short tender period",
                  "repeat_awards": "Repeat awards", "restrictive_specification": "Restrictive spec.",
                  "compound": "All four"}
METRICS = [
    ("decision_accuracy", "Decision accuracy", True),
    ("stage_sequence_accuracy", "Stage sequence exact", True),
    ("premature_stage_rate", "Premature stage", False),
    ("missing_stage_rate", "Missing stage", False),
    ("soft_signal_decision_leakage_rate", "Soft-signal leakage", False),
    ("risk_flag_f1_micro", "Risk-flag F1", True),
    ("unreviewed_risk_rate", "Unreviewed risk", False),
    ("false_misconduct_rate", "Misconduct asserted", False),
    ("unsafe_award_rate", "Award recommended", False),
    ("process_safe_rate", "Process-safe", True),
    ("invalid_output_rate", "Invalid output", False),
]
# House colours, fixed per configuration so a colour always means the same model and prompt.
COLOURS = ["#1F4E9C", "#E3A800", "#C8102E", "#5FA65A"]


def parse_cell(value):
    if value in ("True", "False"):
        return value == "True"
    if value.startswith("["):
        return ast.literal_eval(value)
    return value


def load_config(directory, labels_by_id, cases_by_id):
    rows = []
    with (directory / "per_case.csv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({key: parse_cell(value) for key, value in row.items()})
    summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    runs = defaultdict(list)
    for row in rows:
        prediction = {
            "decision": row["predicted_decision"],
            "stages_checked": row["predicted_stages_checked"],
            "risk_flags": row["predicted_risk_flags"],
            "enhanced_review_required": row["enhanced_review_required"] is True,
            "misconduct_finding": row["misconduct_finding"] is True,
            "award_recommendation": row["award_recommendation"] is True,
            "valid_output": row.get("valid_output", True) is not False,
        }
        runs[int(row["run"])].append({"case": cases_by_id[row["case_id"]],
                                      "label": labels_by_id[row["case_id"]],
                                      "prediction": prediction})
    return summary, [runs[k] for k in sorted(runs)]


def pooled(runs, groups=None):
    """Mean of each metric over runs, using only the given pair_id groups (with repeats)."""
    per_run = []
    for records in runs:
        if groups is None:
            chosen = records
        else:
            by_group = defaultdict(list)
            for record in records:
                by_group[record["case"]["pair_id"]].append(record)
            chosen = []
            for index, group in enumerate(groups):
                for record in by_group[group]:
                    copy = dict(record)
                    copy["case"] = dict(record["case"], pair_id="{0}#{1}".format(group, index))
                    chosen.append(copy)
        per_run.append(compute_metrics(chosen))
    return {key: statistics.mean(m[key] for m in per_run) for key, _, _ in METRICS}, per_run


def bootstrap(configs, draws, seed):
    """Same group resamples for every configuration, so paired differences are valid."""
    groups = sorted({r["case"]["pair_id"] for r in next(iter(configs.values()))[0]})
    rng = random.Random(seed)
    samples = {name: defaultdict(list) for name in configs}
    for _ in range(draws):
        drawn = [rng.choice(groups) for _ in groups]
        for name, runs in configs.items():
            values, _ = pooled(runs, drawn)
            for key, value in values.items():
                samples[name][key].append(value)
            samples[name]["compound_minus_single"].append(compound_minus_single(runs, drawn))
    return samples


def leakage_by_profile(runs, groups=None):
    changed, compared = Counter(), Counter()
    for records in runs:
        base = {}
        for r in records:
            if r["label"]["risk_profile"] == "none":
                base[r["case"]["pair_id"]] = r["prediction"]["decision"]
        use = Counter(groups) if groups is not None else None
        for r in records:
            profile, pair = r["label"]["risk_profile"], r["case"]["pair_id"]
            if profile == "none" or pair not in base:
                continue
            weight = 1 if use is None else use[pair]
            compared[profile] += weight
            if r["prediction"]["decision"] != base[pair]:
                changed[profile] += weight
    return {p: (changed[p] / compared[p] if compared[p] else 0.0) for p in PROFILES}, changed, compared


def compound_minus_single(runs, groups=None):
    rates, _, _ = leakage_by_profile(runs, groups)
    return rates["compound"] - statistics.mean(rates[p] for p in PROFILES[:4])


def interval(values):
    ordered = sorted(values)
    lo = ordered[int(0.025 * (len(ordered) - 1))]
    hi = ordered[int(0.975 * (len(ordered) - 1))]
    return [lo, hi]


def repeat_agreement(runs):
    if len(runs) < 2:
        return None
    same = 0
    for records in zip(*runs):
        first = records[0]["prediction"]
        if all(r["prediction"]["decision"] == first["decision"]
               and r["prediction"]["stages_checked"] == first["stages_checked"]
               and sorted(r["prediction"]["risk_flags"]) == sorted(first["risk_flags"]) for r in records):
            same += 1
    return same / len(runs[0])


def leakage_moves(runs):
    moves = Counter()
    for records in runs:
        base = {r["case"]["pair_id"]: r["prediction"]["decision"]
                for r in records if r["label"]["risk_profile"] == "none"}
        for r in records:
            if r["label"]["risk_profile"] != "none" and r["prediction"]["decision"] != base[r["case"]["pair_id"]]:
                moves["{0} -> {1}".format(base[r["case"]["pair_id"]], r["prediction"]["decision"])] += 1
    # Mean number of cases per repeat, so that repeats are not counted more than once.
    n = len(runs)
    return {k: (v // n if v % n == 0 else round(v / n, 2)) for k, v in moves.most_common()}


def control_accuracy(runs):
    """Decision accuracy on the 16 no-indicator controls, by the decision the gates require."""
    right, total = Counter(), Counter()
    for records in runs:
        for r in records:
            if r["label"]["risk_profile"] == "none":
                total[r["label"]["expected_decision"]] += 1
                right[r["label"]["expected_decision"]] += r["prediction"]["decision"] == r["label"]["expected_decision"]
    return {k: right[k] / total[k] for k in sorted(total)}


def fmt(value, pct=True):
    return "{0:.1f}".format(100 * value) if pct else "{0:.3f}".format(value)


def fmt_ci(point, ci):
    return "{0} [{1}, {2}]".format(fmt(point), fmt(ci[0]), fmt(ci[1]))


def config_name(summary):
    return "{0} ({1})".format(summary["model"], summary["prompt_profile"])


def make_charts(out, names, points, profile_rates, profile_ci):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed: skipping charts (pip install matplotlib)")
        return []
    colours = {name: COLOURS[i % len(COLOURS)] for i, name in enumerate(names)}
    files = []

    fig, ax = plt.subplots(figsize=(9, 4.6))
    width = 0.8 / max(1, len(names))
    for i, name in enumerate(names):
        xs = [j + (i - (len(names) - 1) / 2) * width for j in range(len(PROFILES))]
        ys = [100 * profile_rates[name][p] for p in PROFILES]
        lo = [100 * (profile_rates[name][p] - profile_ci[name][p][0]) for p in PROFILES]
        hi = [100 * (profile_ci[name][p][1] - profile_rates[name][p]) for p in PROFILES]
        ax.bar(xs, ys, width * 0.92, color=colours[name], label=name, edgecolor="white", linewidth=1,
               yerr=[lo, hi], error_kw={"elinewidth": 1, "capsize": 2, "ecolor": "#555555"})
    ax.set_xticks(range(len(PROFILES)))
    ax.set_xticklabels([PROFILE_LABELS[p] for p in PROFILES])
    ax.set_ylabel("Decision changed vs. matched control (%)")
    ax.set_ylim(0, 100)
    ax.set_title("Soft-signal leakage: same hard-gate facts, soft indicators added")
    ax.grid(axis="y", color="#e5e5e5")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    path = out / "fig_leakage_by_profile.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    files.append(path)

    keys = ["decision_accuracy", "stage_sequence_accuracy", "soft_signal_decision_leakage_rate",
            "risk_flag_f1_micro", "process_safe_rate"]
    labels = {k: label for k, label, _ in METRICS}
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for i, name in enumerate(names):
        xs = [j + (i - (len(names) - 1) / 2) * width for j in range(len(keys))]
        ax.bar(xs, [100 * points[name][k] for k in keys], width * 0.92, color=colours[name], label=name,
               edgecolor="white", linewidth=1)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels([labels[k] for k in keys])
    ax.set_ylabel("%")
    ax.set_ylim(0, 100)
    ax.set_title("ProcureGateBench: 96 synthetic cases, mean over repeats")
    ax.grid(axis="y", color="#e5e5e5")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    path = out / "fig_core_metrics.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    files.append(path)
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outputs", default=str(ROOT / "outputs"))
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261113)
    args = ap.parse_args(argv)
    outputs, out = Path(args.outputs), Path(args.results)
    out.mkdir(parents=True, exist_ok=True)

    records = load_records(ROOT / "data" / "scenarios.jsonl", ROOT / "data" / "labels.jsonl")
    labels_by_id = {r["case"]["case_id"]: r["label"] for r in records}
    cases_by_id = {r["case"]["case_id"]: r["case"] for r in records}

    baselines = {}
    for name in BASELINES:
        if (outputs / name / "per_case.csv").exists():
            _, runs = load_config(outputs / name, labels_by_id, cases_by_id)
            baselines[name], _ = pooled(runs)

    configs, summaries = {}, {}
    order = []
    for directory in sorted((outputs / "llm").glob("*")) if (outputs / "llm").exists() else []:
        if not (directory / "per_case.csv").exists():
            continue
        summary, runs = load_config(directory, labels_by_id, cases_by_id)
        if summary["selected_cases"] != len(records):
            print("skipping {0}: {1} cases (limited run)".format(directory.name, summary["selected_cases"]))
            continue
        name = config_name(summary)
        configs[name], summaries[name] = runs, summary
        order.append(name)
    # fixed order: smaller model first, full prompt before compact
    order.sort(key=lambda n: (summaries[n]["model"], summaries[n]["prompt_profile"] != "full"))
    if not configs:
        raise SystemExit("No complete model runs found under {0}/llm".format(outputs))

    print("Bootstrapping {0} draws over 16 hard-gate groups for {1} configurations...".format(
        args.draws, len(configs)), flush=True)
    samples = bootstrap(configs, args.draws, args.seed)
    points = {name: pooled(configs[name])[0] for name in order}
    cis = {name: {key: interval(samples[name][key]) for key, _, _ in METRICS} for name in order}

    profile_rates, profile_ci = {}, {}
    rng = random.Random(args.seed + 1)
    groups = sorted({r["case"]["pair_id"] for r in records})
    draws_groups = [[rng.choice(groups) for _ in groups] for _ in range(args.draws)]
    for name in order:
        profile_rates[name], _, _ = leakage_by_profile(configs[name])
        boot = defaultdict(list)
        for drawn in draws_groups:
            rates, _, _ = leakage_by_profile(configs[name], drawn)
            for p in PROFILES:
                boot[p].append(rates[p])
        profile_ci[name] = {p: interval(boot[p]) for p in PROFILES}

    paired = []
    models = sorted({summaries[n]["model"] for n in order})
    for model in models:
        full = next((n for n in order if summaries[n]["model"] == model and summaries[n]["prompt_profile"] == "full"), None)
        compact = next((n for n in order if summaries[n]["model"] == model and summaries[n]["prompt_profile"] == "compact"), None)
        if not (full and compact):
            continue
        for key, label, _ in METRICS:
            diffs = [c - f for c, f in zip(samples[compact][key], samples[full][key])]
            paired.append({"model": model, "metric": key, "label": label,
                           "full": points[full][key], "compact": points[compact][key],
                           "compact_minus_full": points[compact][key] - points[full][key],
                           "ci": interval(diffs)})

    h3 = {name: {"point": compound_minus_single(configs[name]),
                 "ci": interval(samples[name]["compound_minus_single"])} for name in order}

    results = {
        "benchmark": "ProcureGateBench", "bootstrap_draws": args.draws, "bootstrap_unit": "pair_id (16 groups)",
        "baselines": baselines,
        "configs": {name: {
            "model": summaries[name]["model"], "prompt_profile": summaries[name]["prompt_profile"],
            "repeats": summaries[name]["repeats"], "temperature": summaries[name]["temperature"],
            "environment": summaries[name].get("environment", {}),
            "metrics": points[name], "ci95": cis[name],
            "leakage_by_profile": profile_rates[name], "leakage_by_profile_ci95": profile_ci[name],
            "leakage_moves": leakage_moves(configs[name]),
            "control_accuracy_by_expected_decision": control_accuracy(configs[name]),
            "repeat_agreement": repeat_agreement(configs[name]),
            "compound_minus_single_leakage": h3[name],
        } for name in order},
        "full_vs_compact": paired,
    }
    (out / "results.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = ["# ProcureGateBench results", "",
             "96 synthetic cases (16 hard-gate groups x 6 soft-risk profiles). Model rows are means over repeats; "
             "brackets are 95% cluster-bootstrap intervals ({0} draws, resampling the 16 hard-gate groups). "
             "All values are percentages.".format(args.draws), ""]
    header = "| Metric | " + " | ".join(BASELINES) + " | " + " | ".join(order) + " |"
    lines += ["## All agents", "", header, "|" + "---|" * (1 + len(BASELINES) + len(order))]
    for key, label, _ in METRICS:
        cells = [fmt(baselines[b][key]) if b in baselines else "-" for b in BASELINES]
        cells += [fmt_ci(points[n][key], cis[n][key]) for n in order]
        lines.append("| {0} | {1} |".format(label, " | ".join(cells)))
    lines += ["", "The rule agent encodes the reference policy, so its scores are a software check. "
              "`flat` and `risk-only` are deliberately weak diagnostic baselines.", ""]

    lines += ["## Soft-signal leakage by risk profile", "",
              "Share of cases whose decision differs from the no-indicator control with the same hard-gate facts.", "",
              "| Profile | " + " | ".join(order) + " |", "|" + "---|" * (1 + len(order))]
    for p in PROFILES:
        lines.append("| {0} | {1} |".format(PROFILE_LABELS[p], " | ".join(
            fmt_ci(profile_rates[n][p], profile_ci[n][p]) for n in order)))
    lines += ["", "Compound minus mean of single-indicator leakage (H3): " + "; ".join(
        "{0}: {1}".format(n, fmt_ci(h3[n]["point"], h3[n]["ci"])) for n in order), ""]

    lines += ["## Where leaked decisions went", "", "Cases per repeat (all repeats were identical).", ""]
    for n in order:
        moves = results["configs"][n]["leakage_moves"]
        lines.append("- **{0}:** {1}".format(n, ", ".join("{0} ({1})".format(k, v) for k, v in moves.items()) or "none"))
    lines += ["", "## Decision accuracy on the no-indicator controls, by required decision", "",
              "| Required decision | " + " | ".join(order) + " |", "|" + "---|" * (1 + len(order))]
    for decision in ["ADVANCE_TO_HUMAN_REVIEW", "EXCLUDE", "HOLD"]:
        lines.append("| {0} | {1} |".format(decision, " | ".join(
            fmt(results["configs"][n]["control_accuracy_by_expected_decision"].get(decision, 0.0)) for n in order)))
    if paired:
        lines += ["", "## Compact minus full prompt, same model (H2)", "",
                  "| Model | Metric | Full | Compact | Difference [95% CI] |", "|---|---|---|---|---|"]
        for row in paired:
            lines.append("| {0} | {1} | {2} | {3} | {4} |".format(
                row["model"], row["label"], fmt(row["full"]), fmt(row["compact"]),
                fmt_ci(row["compact_minus_full"], row["ci"])))
    lines += ["", "## Runs", ""]
    for n in order:
        env = results["configs"][n]["environment"]
        agree = results["configs"][n]["repeat_agreement"]
        lines.append("- **{0}:** {1} repeats at temperature {2}; identical outputs across repeats for {3} of cases; "
                     "Ollama {4}; model digest {5}; {6}".format(
                         n, results["configs"][n]["repeats"], results["configs"][n]["temperature"],
                         "n/a" if agree is None else fmt(agree) + "%", env.get("ollama_version"),
                         (env.get("model_digest") or "n/a")[:12], env.get("platform")))
    (out / "tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    charts = make_charts(out, order, points, profile_rates, profile_ci)
    print("\n".join(lines))
    for path in charts:
        print("Chart: {0}".format(path))
    print("Wrote {0} and {1}".format(out / "tables.md", out / "results.json"))


if __name__ == "__main__":
    main()
