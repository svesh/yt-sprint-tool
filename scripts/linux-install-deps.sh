#!/usr/bin/env bash
set -euo pipefail

# Install system and Python build dependencies for Linux builds.
# Creates/updates local .venv and installs pyinstaller + staticx toolchain.

# Ensure Python is available
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 is required to create virtualenv" >&2
  exit 1
fi

# Create venv if missing
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

python -m pip install --upgrade pip wheel setuptools

# Project deps
pip install -r requirements.txt

# System deps helpful for staticx
if command -v apt-get >/dev/null 2>&1; then
  if command -v sudo >/dev/null 2>&1 && [[ "$(id -u)" -ne 0 ]]; then
    sudo apt-get update -y
    sudo apt-get install -y --no-install-recommends patchelf build-essential
  else
    apt-get update -y || true
    apt-get install -y --no-install-recommends patchelf build-essential || true
  fi
fi

# Build toolchain
pip install pyinstaller
pip install "scons>=4.7" --no-cache-dir
pip install --no-build-isolation staticx==0.14.1 --no-cache-dir

echo "Linux build dependencies installed."

