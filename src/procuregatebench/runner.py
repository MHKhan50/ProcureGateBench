"""Dataset loading, repeated runs, resumable model calls and result serialization."""
import csv
import datetime as dt
import json
import platform
import statistics
import sys
import time
from pathlib import Path

from . import __version__
from .agents import MAX_OUTPUT_TOKENS, create_agent
from .metrics import compute_metrics

MODEL_FIELDS = ("decision", "stages_checked", "risk_flags", "enhanced_review_required",
                "misconduct_finding", "award_recommendation", "valid_output")


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
                    if isinstance(value, (int, float)) and not isinstance(value, bool) and key != "n_cases"]
    aggregate = {"n_runs": len(run_metrics), "n_cases_per_run": run_metrics[0]["n_cases"]}
    for key in numeric_keys:
        values = [float(item[key]) for item in run_metrics]
        aggregate[key + "_mean"] = statistics.mean(values)
        aggregate[key + "_stdev"] = statistics.stdev(values) if len(values) > 1 else 0.0
    return aggregate


class CallCache:
    """Append-only JSONL record of model calls, so an interrupted run resumes where it stopped."""

    def __init__(self, path, settings):
        self.path = Path(path)
        self.settings = settings
        self.done = {}
        if self.path.exists():
            for row in read_jsonl(self.path):
                if any(row.get(k) != v for k, v in settings.items()):
                    raise ValueError(
                        "{0} holds calls made with different settings ({1}); use another --output-dir"
                        .format(self.path, ", ".join("{0}={1}".format(k, row.get(k)) for k in settings)))
                self.done[(row["run"], row["case_id"])] = row["prediction"]

    def get(self, run, case_id):
        return self.done.get((run, case_id))

    def add(self, run, case_id, prediction, raw, seconds):
        row = dict(self.settings)
        row.update({"run": run, "case_id": case_id, "prediction": prediction,
                    "raw_response": raw, "seconds": seconds})
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        self.done[(run, case_id)] = prediction


def _call_with_retry(agent, case, attempts=4):
    for attempt in range(attempts):
        try:
            return agent.run(case)
        except Exception as error:  # connection reset, timeout, model still loading
            if attempt == attempts - 1:
                raise RuntimeError(
                    "Model call failed for {0}: {1}. Check that Ollama is running, then run the same "
                    "command again; finished calls are kept.".format(case["case_id"], error)) from None
            time.sleep(10 * (attempt + 1))


def run_experiment(agent_name, cases_path, labels_path, model="qwen2.5:3b",
                   base_url="http://localhost:11434", prompt_profile="full",
                   seed=20261113, temperature=0.0, repeats=1, limit=None,
                   cache_path=None, progress=False):
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least 1")
    records = load_records(cases_path, labels_path)
    if limit is not None:
        records = records[:limit]
    if not records:
        raise ValueError("No cases selected.")
    is_model = agent_name == "ollama"
    started_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    cache = None
    if is_model and cache_path is not None:
        cache = CallCache(cache_path, {"model": model, "prompt_profile": prompt_profile,
                                       "temperature": temperature, "base_seed": seed,
                                       "max_output_tokens": MAX_OUTPUT_TOKENS})
    runtime = {}
    all_run_metrics, all_predictions = [], []
    total_calls, done_calls, timed = repeats * len(records), 0, []
    for run_index in range(repeats):
        run_seed = seed + run_index
        agent = create_agent(agent_name, model=model, base_url=base_url,
                             prompt_profile=prompt_profile, seed=run_seed,
                             temperature=temperature)
        if is_model and not runtime:
            runtime = agent.runtime_info()
        scored_records = []
        for item in records:
            case_id = item["case"]["case_id"]
            prediction = cache.get(run_index + 1, case_id) if cache else None
            if prediction is None:
                result = _call_with_retry(agent, item["case"]) if is_model else agent.run(item["case"])
                prediction = {key: result[key] for key in MODEL_FIELDS if key in result}
                if is_model:
                    timed.append(result.get("seconds", 0.0))
                    if cache:
                        cache.add(run_index + 1, case_id, prediction,
                                  result.get("raw_response", ""), result.get("seconds"))
            done_calls += 1
            if progress and is_model and (done_calls % 12 == 0 or done_calls == total_calls):
                left = ""
                if timed:
                    minutes = statistics.mean(timed) * (total_calls - done_calls) / 60.0
                    left = ", about {0:.0f} min left".format(minutes)
                print("  {0} {1}: {2}/{3} calls{4}".format(model, prompt_profile, done_calls, total_calls, left),
                      flush=True)
            scored_records.append({"case": item["case"], "label": item["label"], "prediction": prediction})
            all_predictions.append({
                "run": run_index + 1,
                "case_id": case_id,
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
                "valid_output": prediction.get("valid_output", True),
            })
        all_run_metrics.append(compute_metrics(scored_records))
    environment = {"python": sys.version.split()[0], "platform": platform.platform(),
                   "started_utc": started_at,
                   "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    environment.update(runtime)
    if timed:
        environment["mean_seconds_per_new_call"] = round(statistics.mean(timed), 3)
    return {
        "benchmark": "ProcureGateBench", "version": __version__, "agent": agent_name,
        "model": model if is_model else None,
        "prompt_profile": prompt_profile if is_model else None,
        "seed": seed, "temperature": temperature if is_model else None,
        "repeats": repeats, "selected_cases": len(records),
        "environment": environment,
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
