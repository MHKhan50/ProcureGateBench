#!/bin/sh
set -eu
python3 -m procuregatebench.cli --agent ollama --model qwen2.5:3b --prompt-profile full --limit 12 --output-dir outputs/qwen-smoke
