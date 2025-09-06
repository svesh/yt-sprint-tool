#!/usr/bin/env bash
set -euo pipefail

# Build Linux binaries for amd64 and arm64 using Docker Buildx
# Outputs: dist/make-sprint-linux-<arch>, dist/default-sprint-linux-<arch>

# Author: Sergei Sveshnikov (svesh87@gmail.com)

ARCHES=(amd64 arm64)
DOCKERFILE="Dockerfile.debian"
DIST_DIR="dist"

mkdir -p "$DIST_DIR"

# Basic checks
if ! command -v docker >/dev/null 2>&1; then
  echo "❌ docker not found. Please install Docker (brew install docker)."
  exit 1
fi

if ! docker buildx version >/dev/null 2>&1; then
  echo "❌ docker buildx not found. Install buildx: brew install docker-buildx (or use a modern docker cli)."
  exit 1
fi

echo "🔧 Using docker context: $(docker context show)"

for arch in "${ARCHES[@]}"; do
  tmp_dir="$DIST_DIR/.tmp-linux-$arch"
  rm -rf "$tmp_dir" && mkdir -p "$tmp_dir"

  echo "🐧 Building Linux $arch ..."
  docker buildx build \
    --platform "linux/$arch" \
    -f "$DOCKERFILE" \
    --build-arg USE_STATICX=1 \
    --target export-stage \
    --output "type=local,dest=$tmp_dir" \
    .

  # Move and rename artifacts to flat dist/
  if [[ -f "$tmp_dir/make-sprint" ]]; then
    mv -f "$tmp_dir/make-sprint" "$DIST_DIR/make-sprint-linux-$arch"
    chmod +x "$DIST_DIR/make-sprint-linux-$arch" || true
  else
    echo "⚠️  make-sprint not found for $arch"
  fi

  if [[ -f "$tmp_dir/default-sprint" ]]; then
    mv -f "$tmp_dir/default-sprint" "$DIST_DIR/default-sprint-linux-$arch"
    chmod +x "$DIST_DIR/default-sprint-linux-$arch" || true
  else
    echo "⚠️  default-sprint not found for $arch"
  fi

  rm -rf "$tmp_dir"
done

echo "✅ Linux builds completed. Artifacts in $DIST_DIR:"
ls -la "$DIST_DIR" | sed -n '1,200p'
