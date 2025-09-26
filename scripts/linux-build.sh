#!/usr/bin/env bash
set -euo pipefail

# Build Linux binaries using PyInstaller + staticx.
# Output: dist/ytsprint-linux-<arch>

DIST_DIR="dist"
mkdir -p "$DIST_DIR"

# Detect architecture
UNAME_M="$(uname -m)"
case "$UNAME_M" in
  x86_64)
    OUT_ARCH="amd64"
    ;;
  aarch64|arm64)
    OUT_ARCH="arm64"
    ;;
  *)
    echo "Unsupported architecture: $UNAME_M" >&2
    exit 1
    ;;
esac

PYTHON_BIN="${PYTHON_BIN:-python}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  else
    echo "Python interpreter not found. Install python3 first." >&2
    exit 1
  fi
fi

echo "Installing build dependencies via pip (pyinstaller, staticx)..."
"$PYTHON_BIN" -m pip install --upgrade pip >/dev/null
"$PYTHON_BIN" -m pip install -r requirements.txt >/dev/null
"$PYTHON_BIN" -m pip install pyinstaller staticx >/dev/null

# Clean previous build artifacts
rm -rf build ytsprint.spec dist/ytsprint dist/ytsprint-static || true

echo "Building Linux binary for arch=$OUT_ARCH..."
pyinstaller --onefile --clean --name ytsprint ytsprint/cli.py

echo "Wrapping binary with staticx..."
staticx dist/ytsprint dist/ytsprint-static

TARGET_PATH="$DIST_DIR/ytsprint-linux-$OUT_ARCH"
mv -f dist/ytsprint-static "$TARGET_PATH"
chmod 0755 "$TARGET_PATH"
rm -f dist/ytsprint

echo "Linux binary available at $TARGET_PATH"
