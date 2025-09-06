#!/usr/bin/env bash
set -euo pipefail

# Build Windows amd64 binaries using Docker + Wine
# Author: Sergei Sveshnikov (svesh87@gmail.com)
# Outputs: dist/make-sprint-windows-amd64.exe, dist/default-sprint-windows-amd64.exe

DOCKERFILE="Dockerfile.windows"
DIST_DIR="dist"

mkdir -p "$DIST_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "❌ docker not found. Please install Docker."
  exit 1
fi

tmp_dir="$DIST_DIR/.tmp-windows-amd64"
rm -rf "$tmp_dir" && mkdir -p "$tmp_dir"

echo "🪟 Building Windows amd64 via Wine Docker (buildx, linux/amd64)..."

if ! docker buildx version >/dev/null 2>&1; then
  echo "❌ docker buildx not found. Install buildx: brew install docker-buildx (or use a modern docker cli)."
  exit 1
fi

docker buildx build \
  --platform linux/amd64 \
  -f "$DOCKERFILE" \
  --target export-stage \
  --output "type=local,dest=$tmp_dir" \
  .

if [[ -f "$tmp_dir/make-sprint.exe" ]]; then
  mv -f "$tmp_dir/make-sprint.exe" "$DIST_DIR/make-sprint-windows-amd64.exe"
else
  echo "⚠️  make-sprint.exe not found"
fi

if [[ -f "$tmp_dir/default-sprint.exe" ]]; then
  mv -f "$tmp_dir/default-sprint.exe" "$DIST_DIR/default-sprint-windows-amd64.exe"
else
  echo "⚠️  default-sprint.exe not found"
fi

rm -rf "$tmp_dir"

echo "✅ Windows amd64 build completed. Artifacts in $DIST_DIR:"
ls -la "$DIST_DIR" | sed -n '1,200p'
