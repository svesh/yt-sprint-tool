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

WINE_TARGET_ARCH="${WINE_TARGET_ARCH:-amd64}"
export WINEARCH="${WINEARCH:-$( [[ "$WINE_TARGET_ARCH" == "x86" ]] && echo win32 || echo win64 )}"
export WINEPREFIX="${WINEPREFIX:-$(pwd)/.wine-python312-$WINE_TARGET_ARCH}"

if ! ensure_cmd wine; then
  echo "wine not found; run scripts/wine-install-deps.sh first" >&2
  exit 2
fi

PY_WIN="C:\\Python312\\python.exe"
REPO_WIN_PATH="$(to_win_path "$(pwd)")"

DIST_DIR="dist"
mkdir -p "$DIST_DIR"

echo "Building Windows executable via PyInstaller (Wine)..."
with_xvfb wine "$PY_WIN" -m PyInstaller --onefile --clean --name ytsprint "${REPO_WIN_PATH}\\ytsprint\\cli.py"

# Move artifact from dist/ to expected name
if [[ -f dist/ytsprint.exe ]]; then
  suffix="$WINE_TARGET_ARCH"
  [[ "$suffix" == "x86" ]] && suffix="x86" || suffix="amd64"
  mv -f dist/ytsprint.exe "$DIST_DIR/ytsprint-windows-${suffix}.exe"
fi

echo "Done. Artifacts in $DIST_DIR:"
ls -la "$DIST_DIR" | sed -n '1,200p'
