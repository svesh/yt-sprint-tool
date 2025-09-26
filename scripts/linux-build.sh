#!/usr/bin/env bash
set -euo pipefail

# Build Linux binaries natively (no Docker) using PyInstaller
# and always wrap with staticx for static executables.
# Outputs: dist/make-sprint-linux-<arch>, dist/default-sprint-linux-<arch>

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

echo "Building Linux binaries for arch=$OUT_ARCH..."
pyinstaller --onefile --clean --name make-sprint ytsprint/make_sprint.py
pyinstaller --onefile --clean --name default-sprint ytsprint/default_sprint.py

echo "Wrapping binaries with staticx..."
staticx dist/make-sprint dist/make-sprint-static
staticx dist/default-sprint dist/default-sprint-static

# Move to expected names
install -m 0755 dist/make-sprint-static "$DIST_DIR/make-sprint-linux-$OUT_ARCH"
install -m 0755 dist/default-sprint-static "$DIST_DIR/default-sprint-linux-$OUT_ARCH"

# Remove intermediate binaries to keep the directory tidy
rm -f dist/make-sprint dist/default-sprint dist/make-sprint-static dist/default-sprint-static

echo "Done. Artifacts in $DIST_DIR:"
ls -la "$DIST_DIR" | sed -n '1,200p'
