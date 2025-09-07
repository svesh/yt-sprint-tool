#!/usr/bin/env bash
set -euo pipefail

# Install system and Python build dependencies for Linux builds.
# Creates/updates local .venv and installs pyinstaller + staticx toolchain.

# Consolidated apt-get pass (faster): install Python + build deps in one go
if command -v apt-get >/dev/null 2>&1; then
  echo "Installing system packages via apt-get (python + build deps)..."
  apt-get update -y || true
  apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip python3-dev \
    patchelf build-essential || true
else
  # If apt-get is unavailable and python3 is missing, we cannot proceed.
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found and no apt-get available. Aborting." >&2
    exit 1
  fi
fi

# Create venv if missing, preferring system /usr/bin/python3
if [[ ! -d .venv ]]; then
  PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"
  if [[ ! -x "$PYTHON_BIN" ]]; then
    PYTHON_BIN="$(command -v python3)"
  fi
  echo "Creating virtualenv with: $PYTHON_BIN"
  "$PYTHON_BIN" -m venv .venv
fi
source .venv/bin/activate

python -m pip install --upgrade pip wheel setuptools

# Project deps
pip install -r requirements.txt

# Build toolchain
pip install "scons>=4.7" --no-cache-dir
pip install --no-build-isolation staticx==0.14.1 --no-cache-dir

echo "Linux build dependencies installed."
