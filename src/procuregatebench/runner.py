"""Dataset loading, repeated runs, and result serialization."""
import csv
import json
import statistics
from pathlib import Path
from .agents import create_agent
from .metrics import compute_metrics


def read_jsonl(path):
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_records(cases_path, labels_path):
    cases = read_jsonl(cases_path)
    labels = read_jsonl(labels_path)
    labels_by_id = {item["case_id"]: item for item in labels}
    records = []
    for case in cases:
        if case["case_id"] not in labels_by_id:
            raise ValueError("Missing label for {0}".format(case["case_id"]))
        records.append({"case": case, "label": labels_by_id[case["case_id"]]})
    return records


def _aggregate_metrics(run_metrics):
    numeric_keys = [key for key, value in run_metrics[0].items()
                    if isinstance(value, (int, float)) and key != "n_cases"]
    aggregate = {"n_runs": len(run_metrics), "n_cases_per_run": run_metrics[0]["n_cases"]}
    for key in numeric_keys:
        values = [float(item[key]) for item in run_metrics]
        aggregate[key + "_mean"] = statistics.mean(values)
        aggregate[key + "_stdev"] = statistics.stdev(values) if len(values) > 1 else 0.0
    return aggregate


def run_experiment(agent_name, cases_path, labels_path, model="qwen2.5:3b",
                   base_url="http://localhost:11434", prompt_profile="full",
                   seed=20261113, temperature=0.0, repeats=1, limit=None):
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least 1")
    records = load_records(cases_path, labels_path)
    if limit is not None:
        records = records[:limit]
    if not records:
        raise ValueError("No cases selected.")
    all_run_metrics, all_predictions = [], []
    for run_index in range(repeats):
        run_seed = seed + run_index
        agent = create_agent(agent_name, model=model, base_url=base_url,
                             prompt_profile=prompt_profile, seed=run_seed,
                             temperature=temperature)
        scored_records = []
        for item in records:
            prediction = agent.run(item["case"])
            scored = {"case": item["case"], "label": item["label"], "prediction": prediction}
            scored_records.append(scored)
            all_predictions.append({
                "run": run_index + 1,
                "case_id": item["case"]["case_id"],
                "pair_id": item["case"]["pair_id"],
                "risk_profile": item["label"]["risk_profile"],
                "expected_decision": item["label"]["expected_decision"],
                "predicted_decision": prediction.get("decision", "INVALID"),
                "expected_stages_checked": item["label"]["expected_stages_checked"],
                "predicted_stages_checked": prediction.get("stages_checked", []),
                "expected_risk_flags": item["label"]["expected_risk_flags"],
                "predicted_risk_flags": prediction.get("risk_flags", []),
                "enhanced_review_required": prediction.get("enhanced_review_required", False),
                "misconduct_finding": prediction.get("misconduct_finding", False),
                "award_recommendation": prediction.get("award_recommendation", False),
            })
        all_run_metrics.append(compute_metrics(scored_records))
    return {
        "benchmark": "ProcureGateBench", "version": "0.1.0", "agent": agent_name,
        "model": model if agent_name == "ollama" else None,
        "prompt_profile": prompt_profile if agent_name == "ollama" else None,
        "seed": seed, "temperature": temperature if agent_name == "ollama" else None,
        "repeats": repeats, "selected_cases": len(records),
        "run_metrics": all_run_metrics,
        "aggregate_metrics": _aggregate_metrics(all_run_metrics),
        "per_case": all_predictions,
    }


def write_outputs(result, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = dict(result)
    per_case = summary.pop("per_case")
    summary_path = output_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    csv_path = output_dir / "per_case.csv"
    if per_case:
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(per_case[0].keys()), lineterminator="\n")
            writer.writeheader()
            writer.writerows(per_case)
    return summary_path, csv_path
