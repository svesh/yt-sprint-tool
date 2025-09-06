#!/usr/bin/env bash
set -euo pipefail

# Build macOS native binaries for the current host arch (arm64 or x86_64)
# Author: Sergei Sveshnikov (svesh87@gmail.com)
# Outputs: dist/make-sprint-macos-<arch>, dist/default-sprint-macos-<arch>

DIST_DIR="dist"
mkdir -p "$DIST_DIR"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "❌ This script must be run on macOS."
  exit 1
fi

if [[ ! -d .venv ]]; then
  echo "❌ .venv not found. Create venv and install dependencies first."
  exit 1
fi

source .venv/bin/activate

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "❌ PyInstaller is not available in .venv. Install it (pip install pyinstaller)."
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
    echo "❌ Unsupported host arch: $HOST_UNAME_ARCH (expected arm64 or x86_64)" >&2
    exit 1
    ;;
esac

echo "🍎 Building macOS native binaries for $TARGET_ARCH_FLAG..."

rm -rf build dist/*.spec || true

pyinstaller --onefile --clean --target-arch "$TARGET_ARCH_FLAG" --name make-sprint ytsprint/make_sprint.py
pyinstaller --onefile --clean --target-arch "$TARGET_ARCH_FLAG" --name default-sprint ytsprint/default_sprint.py

mv -f dist/make-sprint "$DIST_DIR/make-sprint-$OUT_SUFFIX"
mv -f dist/default-sprint "$DIST_DIR/default-sprint-$OUT_SUFFIX"

echo "✅ macOS native build completed. Artifacts in $DIST_DIR:"
ls -la "$DIST_DIR" | sed -n '1,200p'
