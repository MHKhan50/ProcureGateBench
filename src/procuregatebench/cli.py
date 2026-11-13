"""Command-line entry point."""
import argparse
from pathlib import Path
from .runner import run_experiment, write_outputs


def build_parser():
    parser = argparse.ArgumentParser(description="Run the ProcureGateBench synthetic process-safety benchmark.")
    parser.add_argument("--agent", choices=["rule", "flat", "risk-only", "ollama"], default="rule")
    parser.add_argument("--model", default="qwen2.5:3b")
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--prompt-profile", choices=["full", "compact"], default="full")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=20261113)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--cases", default=None)
    parser.add_argument("--labels", default=None)
    parser.add_argument("--output-dir", default=None)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    cases_path = Path(args.cases) if args.cases else root / "data" / "scenarios.jsonl"
    labels_path = Path(args.labels) if args.labels else root / "data" / "labels.jsonl"
    if args.output_dir:
        output_dir = Path(args.output_dir)
    elif args.agent == "ollama":
        safe_model = args.model.replace(":", "-").replace("/", "-")
        output_dir = root / "outputs" / "llm" / "{0}_{1}".format(safe_model, args.prompt_profile)
    else:
        output_dir = root / "outputs" / args.agent
    cache_path = output_dir / "calls.jsonl" if args.agent == "ollama" else None
    result = run_experiment(
        agent_name=args.agent, cases_path=cases_path, labels_path=labels_path,
        model=args.model, base_url=args.base_url, prompt_profile=args.prompt_profile,
        seed=args.seed, temperature=args.temperature, repeats=args.repeats, limit=args.limit,
        cache_path=cache_path, progress=True,
    )
    summary_path, csv_path = write_outputs(result, output_dir)
    print("Agent: {0}".format(args.agent))
    print("Cases per run: {0}".format(result["selected_cases"]))
    print("Runs: {0}".format(result["repeats"]))
    print("Aggregate metrics:")
    for key, value in sorted(result["aggregate_metrics"].items()):
        if key.endswith("_mean"):
            print("  {0}: {1:.4f}".format(key[:-5], value))
    print("Summary: {0}".format(summary_path))
    print("Per-case CSV: {0}".format(csv_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
