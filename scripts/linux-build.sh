#!/usr/bin/env bash
set -euo pipefail

# Build Linux binaries natively (no Docker) using PyInstaller
# and always wrap with staticx for static executables.
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

if [[ ! -d .venv ]]; then
  echo ".venv not found. Run scripts/linux-install-deps.sh first." >&2
  exit 2
fi
source .venv/bin/activate

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "pyinstaller not found in .venv. Run scripts/linux-install-deps.sh." >&2
  exit 2
fi
if ! command -v staticx >/dev/null 2>&1; then
  echo "staticx not found in .venv. Run scripts/linux-install-deps.sh." >&2
  exit 2
fi

# Clean previous build artifacts
rm -rf build dist/*.spec || true

echo "Building Linux binary for arch=$OUT_ARCH..."
pyinstaller --onefile --clean --name ytsprint ytsprint/cli.py

echo "Wrapping binary with staticx..."
staticx dist/ytsprint dist/ytsprint-static

# Move to expected name
install -m 0755 dist/ytsprint-static "$DIST_DIR/ytsprint-linux-$OUT_ARCH"

# Remove intermediate binaries to keep the directory tidy
rm -f dist/ytsprint dist/ytsprint-static

echo "Done. Artifacts in $DIST_DIR:"
ls -la "$DIST_DIR" | sed -n '1,200p'
