#!/bin/bash
# Render a list of shots sequentially (resumable). Usage: worker.sh <threads> <shot> [shot...]
cd "$(dirname "$0")"
T=$1; shift
for s in "$@"; do
  python3 render_shot.py "$s" --threads "$T" 2>&1 | grep -E "DONE|Traceback|Error:" 
done
