#!/usr/bin/env bash
set -euo pipefail

# Build Windows executables under Wine, assuming wine-install-deps.sh already ran.

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This script is intended for Linux hosts." >&2
  exit 1
fi

ensure_cmd() { command -v "$1" >/dev/null 2>&1; }

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

export WINEARCH="${WINEARCH:-win64}"
export WINEPREFIX="${WINEPREFIX:-$(pwd)/.wine-python312}"

if ! ensure_cmd wine; then
  echo "wine not found; run scripts/wine-install-deps.sh first" >&2
  exit 2
fi

PY_WIN="C:\\Python312\\python.exe"
REPO_WIN_PATH="$(to_win_path "$(pwd)")"

DIST_DIR="dist"
mkdir -p "$DIST_DIR"

echo "Building Windows executables via PyInstaller (Wine)..."
with_xvfb wine "$PY_WIN" -m PyInstaller --onefile --clean --name make-sprint "${REPO_WIN_PATH}\\ytsprint\\make_sprint.py"
with_xvfb wine "$PY_WIN" -m PyInstaller --onefile --clean --name default-sprint "${REPO_WIN_PATH}\\ytsprint\\default_sprint.py"

# Move artifacts from dist/ to expected names
if [[ -f dist/make-sprint.exe ]]; then
  mv -f dist/make-sprint.exe "$DIST_DIR/make-sprint-windows-amd64.exe"
fi
if [[ -f dist/default-sprint.exe ]]; then
  mv -f dist/default-sprint.exe "$DIST_DIR/default-sprint-windows-amd64.exe"
fi

echo "Done. Artifacts in $DIST_DIR:"
ls -la "$DIST_DIR" | sed -n '1,200p'

