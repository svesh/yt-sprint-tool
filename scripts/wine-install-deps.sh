#!/usr/bin/env bash
set -euo pipefail

# Install Wine + Windows Python under Wine and project build deps.
# Mirrors the working approach from tobix/pywine images, adapted for Ubuntu runners.

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This script is intended for Linux hosts." >&2
  exit 1
fi

ensure_cmd() { command -v "$1" >/dev/null 2>&1; }

run_as_root() {
  if ensure_cmd sudo && [[ "$(id -u)" -ne 0 ]]; then
    sudo "$@"
  else
    "$@"
  fi
}

with_xvfb() {
  if command -v xvfb-run >/dev/null 2>&1; then
    xvfb-run -a "$@"
  else
    "$@"
  fi
}

to_win_path() {
  if command -v winepath >/dev/null 2>&1; then
    winepath -w "$1"
  else
    printf 'Z:\\\\%s' "$(realpath "$1" | sed 's|/|\\\\|g')"
  fi
}

export DEBIAN_FRONTEND=noninteractive

echo "Installing system packages (Wine, Xvfb, helpers)..."
run_as_root dpkg --add-architecture i386 || true
run_as_root apt-get update -y
if apt-cache show wine >/dev/null 2>&1; then
  run_as_root apt-get install -y --no-install-recommends \
    wine wine64 wine32:i386 winbind cabextract curl ca-certificates \
    xvfb xauth unzip libvulkan1
else
  run_as_root apt-get install -y --no-install-recommends \
    wine64 wine32:i386 winbind cabextract curl ca-certificates \
    xvfb xauth unzip libvulkan1 || true
fi

# Patch xvfb-run to ensure Xvfb is properly waited on (mirrors base wine image)
if ! grep -q 'wait "$XVFBPID"' /usr/bin/xvfb-run 2>/dev/null; then
  run_as_root sed -i '/kill ".*"/a \
        wait "$XVFBPID" >>"$ERRORFILE" 2>&1' /usr/bin/xvfb-run || true
fi

export WINEARCH="win64"
export WINEPREFIX="$(pwd)/.wine-python312"
mkdir -p "$WINEPREFIX"

echo "Initializing Wine prefix..."
if ensure_cmd wineboot; then
  with_xvfb wineboot -i || true
fi

# Prepare environment: disable menu updates, Mono & Gecko like pywine
umask 0
export WINEDEBUG="-all"
export WINEDLLOVERRIDES="winemenubuilder.exe,mscoree,mshtml="
with_xvfb sh -c "\
  wine reg add 'HKCU\\Software\\Wine\\DllOverrides' /v winemenubuilder.exe /t REG_SZ /d '' /f && \
  wine reg add 'HKCU\\Software\\Wine\\DllOverrides' /v mscoree /t REG_SZ /d '' /f && \
  wine reg add 'HKCU\\Software\\Wine\\DllOverrides' /v mshtml /t REG_SZ /d '' /f && \
  wineserver -w"

PY_VER="3.12.7"
PY_SUFFIX="amd64"
PY_INSTALLER="python-${PY_VER}-${PY_SUFFIX}.exe"
PY_URL="https://www.python.org/ftp/python/${PY_VER}/${PY_INSTALLER}"

CACHE_DIR=".cache/wine-python"
mkdir -p "$CACHE_DIR"

if [[ ! -f "$CACHE_DIR/$PY_INSTALLER" ]]; then
  echo "Downloading $PY_INSTALLER ..."
  curl -fsSL "$PY_URL" -o "$CACHE_DIR/$PY_INSTALLER"
fi

echo "Installing Windows Python under Wine..."
with_xvfb wine start /wait "$(to_win_path "$CACHE_DIR/$PY_INSTALLER")" \
  /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 TargetDir=C:\\Python312 || true

PY_WIN="C:\\Python312\\python.exe"

echo "Verifying Python installation under Wine..."
with_xvfb wine "$PY_WIN" -V || {
  echo "Windows Python not available under Wine; installation failed" >&2
  exit 3
}

REPO_WIN_PATH="$(to_win_path "$(pwd)")"

echo "Installing project deps and PyInstaller inside Wine..."
with_xvfb wine "$PY_WIN" -m pip install --upgrade pip wheel setuptools
with_xvfb wine "$PY_WIN" -m pip install -r "${REPO_WIN_PATH}\\requirements.txt"
with_xvfb wine "$PY_WIN" -m pip install pyinstaller

echo "Wine build dependencies installed."
