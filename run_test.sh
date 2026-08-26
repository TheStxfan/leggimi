#!/usr/bin/env bash

clear 2>/dev/null || true

cd "$(dirname "$0")" || exit 1

source .venv/bin/activate

pytest -rs