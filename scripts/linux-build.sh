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

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "pyinstaller not found. Install it via pip (see README)." >&2
  exit 1
fi

if ! command -v staticx >/dev/null 2>&1; then
  echo "staticx not found. Install it via pip (see README)." >&2
  exit 1
fi

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
ls -la dist
