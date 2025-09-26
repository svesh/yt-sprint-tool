#!/usr/bin/env bash
set -euo pipefail

# Build Linux binaries via Docker.
# Usage: scripts/build-linux-docker.sh [--arch amd64|arm64|all]
# Default: build both amd64 and arm64 sequentially.

ARCHES=(amd64 arm64)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --arch)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --arch requires a value (amd64|arm64|all)" >&2
        exit 1
      fi
      case "$2" in
        amd64) ARCHES=(amd64) ;;
        arm64) ARCHES=(arm64) ;;
        all)   ARCHES=(amd64 arm64) ;;
        *) echo "Unknown arch: $2" >&2; exit 1 ;;
      esac
      shift 2
      ;;
    amd64|arm64)
      ARCHES=("$1")
      shift
      ;;
    all)
      ARCHES=(amd64 arm64)
      shift
      ;;
    -h|--help)
      cat <<'USAGE'
Usage: scripts/build-linux-docker.sh [--arch amd64|arm64|all]
Build Linux binaries via Docker using Dockerfile.build.
If no options are provided, both architectures are built sequentially.
USAGE
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

DIST_DIR="dist"
mkdir -p "$DIST_DIR"

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: Missing dependency: $1" >&2
    exit 1
  fi
}

require docker
if ! docker buildx version >/dev/null 2>&1; then
  echo "ERROR: docker buildx not found. Install or enable buildx." >&2
  exit 1
fi

build_linux() {
  local arch="$1"; local tmp_dir="$DIST_DIR/.tmp-linux-$arch";
  local artifact="$DIST_DIR/ytsprint-linux-$arch"
  rm -rf "$tmp_dir" && mkdir -p "$tmp_dir"
  rm -f "$artifact"
  echo "Building Linux $arch via Docker (Dockerfile.build)..."
  docker buildx build \
    --platform "linux/$arch" \
    -f Dockerfile.build \
    --target export \
    --output "type=local,dest=$tmp_dir" \
    .
  if [[ -f "$tmp_dir/ytsprint-linux-$arch" ]]; then
    mv -f "$tmp_dir/ytsprint-linux-$arch" "$artifact"
    chmod +x "$artifact" || true
  elif [[ -f "$tmp_dir/ytsprint" ]]; then
    mv -f "$tmp_dir/ytsprint" "$artifact"
    chmod +x "$artifact" || true
  else
    echo "Warning: ytsprint binary not found for $arch"
  fi
  rm -rf "$tmp_dir"
}

for arch in "${ARCHES[@]}"; do
  build_linux "$arch"
done

echo "Docker builds completed. See ./dist"
ls -la "$DIST_DIR" | sed -n '1,200p'
