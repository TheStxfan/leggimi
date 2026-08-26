#!/usr/bin/env bash

clear 2>/dev/null || true

set -euo pipefail

# Vai alla cartella del progetto (dove sta questo script)
cd "$(dirname "$0")" || exit 1

# Attiva il virtual environment locale
source .venv/bin/activate

# Rendi il package `leggimi` importabile da qualsiasi punto
export PYTHONPATH="src:${PYTHONPATH:-}"


SCRIPT="main"
# SCRIPT="extractor"
# SCRIPT="llm_client"
# SCRIPT="scriptgen"
# SCRIPT="tts"
# SCRIPT="test_audio"

if [ "$SCRIPT" = "main" ]; then
    python main.py
else
    python -m "leggimi.${SCRIPT}"
fi