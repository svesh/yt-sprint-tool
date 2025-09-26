#!/usr/bin/env bash
set -euo pipefail

# Install system dependencies required for building Linux binaries.

if ! command -v apt-get >/dev/null 2>&1; then
  echo "apt-get not found; skipping system dependency installation." >&2
  exit 0
fi

SUDO=""
if [[ $EUID -ne 0 ]]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  else
    echo "This script requires root privileges or sudo to run apt-get." >&2
    exit 1
  fi
fi

export DEBIAN_FRONTEND=noninteractive

$SUDO apt-get update -y
$SUDO apt-get install -y --no-install-recommends \
  python3 \
  python3-venv \
  python3-pip \
  python3-dev \
  build-essential \
  patchelf
