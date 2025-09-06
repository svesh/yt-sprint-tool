#!/usr/bin/env bash
set -euo pipefail

# Publish multi-arch image (linux/arm64 + linux/amd64) to GHCR using builder 'cross'.
# Author: Sergei Sveshnikov (svesh87@gmail.com)
# Requires: buildx builder 'cross' with aarch64 and amd64 nodes (see OSX_BUILD.md).

IMAGE=${IMAGE:-}
TAG=${TAG:-latest}
GHCR_USER=${GHCR_USER:-}
GHCR_TOKEN=${GHCR_TOKEN:-}

if [[ -z "$IMAGE" || -z "$GHCR_USER" || -z "$GHCR_TOKEN" ]]; then
  echo "Usage: export IMAGE=ghcr.io/<owner>/<repo> GHCR_USER=<user> GHCR_TOKEN=<token> [TAG=latest]; $0"
  exit 1
fi

echo "🔐 Logging into GHCR as $GHCR_USER"
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

echo "🔨 Building and pushing multi-arch image: $IMAGE:$TAG"
docker buildx build \
  --builder cross \
  --platform linux/arm64,linux/amd64 \
  -f Dockerfile.linux \
  -t "$IMAGE:$TAG" \
  --push .

echo "✅ Done. Inspecting manifest: $IMAGE:$TAG"
docker buildx imagetools inspect "$IMAGE:$TAG" | sed -n '1,120p'
