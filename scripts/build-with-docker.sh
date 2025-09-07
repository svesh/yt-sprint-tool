#!/usr/bin/env bash
set -euo pipefail

# Build binaries via Docker locally without calling other scripts.
# Usage: scripts/build-with-docker.sh [target]
# target: all (default) | linux-amd64 | linux-arm64 | windows-amd64 | windows-x86

TARGET="${1:-all}"
DIST_DIR="dist"
mkdir -p "$DIST_DIR"

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "❌ Missing dependency: $1" >&2
    exit 1
  fi
}

require docker
if ! docker buildx version >/dev/null 2>&1; then
  echo "❌ docker buildx not found. Install or enable buildx." >&2
  exit 1
fi

build_linux() {
  local arch="$1"; local tmp_dir="$DIST_DIR/.tmp-linux-$arch";
  rm -rf "$tmp_dir" && mkdir -p "$tmp_dir"
  echo "🐧 Building Linux $arch via Docker (unified Dockerfile, FLAVOR=linux)..."
  docker buildx build \
    --platform "linux/$arch" \
    -f Dockerfile \
    --build-arg FLAVOR=linux \
    --target export \
    --output "type=local,dest=$tmp_dir" \
    .
  if [[ -f "$tmp_dir/make-sprint-linux-$arch" ]]; then
    mv -f "$tmp_dir/make-sprint-linux-$arch" "$DIST_DIR/make-sprint-linux-$arch"
    chmod +x "$DIST_DIR/make-sprint-linux-$arch" || true
  elif [[ -f "$tmp_dir/make-sprint" ]]; then
    mv -f "$tmp_dir/make-sprint" "$DIST_DIR/make-sprint-linux-$arch"
    chmod +x "$DIST_DIR/make-sprint-linux-$arch" || true
  else
    echo "⚠️  make-sprint not found for $arch"
  fi
  if [[ -f "$tmp_dir/default-sprint-linux-$arch" ]]; then
    mv -f "$tmp_dir/default-sprint-linux-$arch" "$DIST_DIR/default-sprint-linux-$arch"
    chmod +x "$DIST_DIR/default-sprint-linux-$arch" || true
  elif [[ -f "$tmp_dir/default-sprint" ]]; then
    mv -f "$tmp_dir/default-sprint" "$DIST_DIR/default-sprint-linux-$arch"
    chmod +x "$DIST_DIR/default-sprint-linux-$arch" || true
  else
    echo "⚠️  default-sprint not found for $arch"
  fi
  rm -rf "$tmp_dir"
}

build_windows_amd64() {
  local tmp_dir="$DIST_DIR/.tmp-windows-amd64";
  rm -rf "$tmp_dir" && mkdir -p "$tmp_dir"
  echo "🪟 Building Windows amd64 via Docker + Wine (unified Dockerfile, FLAVOR=wine)..."
  docker buildx build \
    --platform linux/amd64 \
    -f Dockerfile \
    --build-arg FLAVOR=wine \
    --target export \
    --output "type=local,dest=$tmp_dir" \
    .
  # Support both plain names and suffixed names from wine-build.sh
  if [[ -f "$tmp_dir/make-sprint-windows-amd64.exe" ]]; then
    mv -f "$tmp_dir/make-sprint-windows-amd64.exe" "$DIST_DIR/make-sprint-windows-amd64.exe"
  elif [[ -f "$tmp_dir/make-sprint.exe" ]]; then
    mv -f "$tmp_dir/make-sprint.exe" "$DIST_DIR/make-sprint-windows-amd64.exe"
  else
    echo "⚠️  make-sprint(.exe) not found in $tmp_dir"
  fi
  if [[ -f "$tmp_dir/default-sprint-windows-amd64.exe" ]]; then
    mv -f "$tmp_dir/default-sprint-windows-amd64.exe" "$DIST_DIR/default-sprint-windows-amd64.exe"
  elif [[ -f "$tmp_dir/default-sprint.exe" ]]; then
    mv -f "$tmp_dir/default-sprint.exe" "$DIST_DIR/default-sprint-windows-amd64.exe"
  else
    echo "⚠️  default-sprint(.exe) not found in $tmp_dir"
  fi
  rm -rf "$tmp_dir"
}

case "$TARGET" in
  all)
    build_linux amd64
    build_linux arm64
    build_windows_amd64
    ;;
  linux-amd64)
    build_linux amd64
    ;;
  linux-arm64)
    build_linux arm64
    ;;
  windows-amd64)
    build_windows_amd64
    ;;
  windows-x86)
    echo "Windows x86 target is not supported yet via Docker." >&2
    exit 2
    ;;
  *)
    echo "Unknown target: $TARGET" >&2
    exit 1
    ;;
esac

echo "✅ Docker builds completed. See ./dist"
ls -la "$DIST_DIR" | sed -n '1,200p'
