#!/usr/bin/env bash
set -euo pipefail

# Build macOS native binary for the current host arch (arm64 or x86_64)
# Author: Sergei Sveshnikov (svesh87@gmail.com)
# Output: dist/ytsprint-macos-<arch>

DIST_DIR="dist"
mkdir -p "$DIST_DIR"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "ERROR: This script must be run on macOS."
  exit 1
fi

if [[ ! -d .venv ]]; then
  echo "ERROR: .venv not found. Create venv and install dependencies first."
  exit 1
fi

source .venv/bin/activate

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "ERROR: PyInstaller is not available in .venv. Install it (pip install pyinstaller)."
  exit 1
fi

HOST_UNAME_ARCH="$(uname -m)"
case "$HOST_UNAME_ARCH" in
  arm64)
    TARGET_ARCH_FLAG="arm64"
    OUT_SUFFIX="macos-arm64"
    ;;
  x86_64)
    TARGET_ARCH_FLAG="x86_64"
    OUT_SUFFIX="macos-x86_64"
    ;;
  *)
    echo "ERROR: Unsupported host arch: $HOST_UNAME_ARCH (expected arm64 or x86_64)" >&2
    exit 1
    ;;
esac

echo "Building macOS native binary for $TARGET_ARCH_FLAG..."

rm -rf build dist/*.spec || true

pyinstaller --onefile --clean --target-arch "$TARGET_ARCH_FLAG" --name ytsprint ytsprint/cli.py

mv -f dist/ytsprint "$DIST_DIR/ytsprint-$OUT_SUFFIX"

echo "macOS native build completed. Artifacts in $DIST_DIR:"
ls -la "$DIST_DIR" | sed -n '1,200p'
