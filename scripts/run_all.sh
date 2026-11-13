#!/bin/sh
# Full ProcureGateBench study on a local machine with Ollama.
# Two models x two prompt profiles x 3 repeats x 96 cases = 1,152 model calls.
# Every call is saved as it finishes; if the run stops, run this script again and it resumes.
set -eu
cd "$(dirname "$0")/.."
export PYTHONPATH=src
MODELS="${MODELS:-qwen2.5:3b llama3.1:8b}"
REPEATS="${REPEATS:-3}"

if ! curl -s http://localhost:11434/api/version >/dev/null; then
  echo "Ollama is not running. Open the Ollama app (or run: ollama serve) and try again."
  exit 1
fi
for m in $MODELS; do
  if ! ollama list | awk 'NR>1 {print $1}' | grep -qx "$m"; then
    echo "Model $m is not installed. Run: ollama pull $m"
    exit 1
  fi
done

python3 -m unittest discover -s tests
for agent in rule flat risk-only; do
  python3 -m procuregatebench.cli --agent "$agent" >/dev/null
done
echo "Baselines done."

for m in $MODELS; do
  for profile in full compact; do
    echo "== $m, $profile prompt, $REPEATS repeats"
    python3 -m procuregatebench.cli --agent ollama --model "$m" --prompt-profile "$profile" \
      --temperature 0 --repeats "$REPEATS" | grep -E "calls|decision_accuracy|soft_signal"
  done
done

python3 scripts/analysis.py
