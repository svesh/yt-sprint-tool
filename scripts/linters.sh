#!/usr/bin/env bash
set -euo pipefail

echo "==> Activating venv"
if [[ ! -d .venv ]]; then
  echo "ERROR: .venv not found. Create it: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi
source .venv/bin/activate

echo "==> pylint"
pylint **/*.py

echo "==> pyright"
pyright

echo "==> isort (check)"
python -m isort --check --diff .

echo "==> markdown lint"
pymarkdownlnt --config .pymarkdownlnt.json scan --recurse --exclude=./.venv .

echo "==> yamllint"
yamllint -c .yamllint.yaml .

echo "==> pytest"
pytest -v

echo "==> helm lint (conditional)"
if command -v helm >/dev/null 2>&1 && [[ -d helm ]]; then
  helm lint helm/
else
  echo "(skip) helm or helm/ not present"
fi

echo "All checks completed successfully"
