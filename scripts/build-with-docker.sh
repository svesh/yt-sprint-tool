#!/usr/bin/env bash
set -euo pipefail

# Build binaries via Docker locally without calling other scripts.
# Usage: scripts/build-with-docker.sh [target]
# target: all (default) | linux-amd64 | linux-arm64 | windows-amd64 | windows-x86 | runtime | runtime-amd64 | runtime-arm64

TARGET="${1:-all}"
DIST_DIR="dist"
mkdir -p "$DIST_DIR"
rm -f "$DIST_DIR"/make-sprint "$DIST_DIR"/default-sprint

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
  rm -rf "$tmp_dir" && mkdir -p "$tmp_dir"
  echo "Building Linux $arch via Docker (unified Dockerfile, FLAVOR=linux)..."
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
    echo "Warning: make-sprint not found for $arch"
  fi
  if [[ -f "$tmp_dir/default-sprint-linux-$arch" ]]; then
    mv -f "$tmp_dir/default-sprint-linux-$arch" "$DIST_DIR/default-sprint-linux-$arch"
    chmod +x "$DIST_DIR/default-sprint-linux-$arch" || true
  elif [[ -f "$tmp_dir/default-sprint" ]]; then
    mv -f "$tmp_dir/default-sprint" "$DIST_DIR/default-sprint-linux-$arch"
    chmod +x "$DIST_DIR/default-sprint-linux-$arch" || true
  else
    echo "Warning: default-sprint not found for $arch"
  fi
  rm -rf "$tmp_dir"
}

build_windows_amd64() {
  local tmp_dir="$DIST_DIR/.tmp-windows-amd64";
  rm -rf "$tmp_dir" && mkdir -p "$tmp_dir"
  echo "Building Windows amd64 via Docker + Wine (unified Dockerfile, FLAVOR=wine)..."
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
    echo "Warning: make-sprint(.exe) not found in $tmp_dir"
  fi
  if [[ -f "$tmp_dir/default-sprint-windows-amd64.exe" ]]; then
    mv -f "$tmp_dir/default-sprint-windows-amd64.exe" "$DIST_DIR/default-sprint-windows-amd64.exe"
  elif [[ -f "$tmp_dir/default-sprint.exe" ]]; then
    mv -f "$tmp_dir/default-sprint.exe" "$DIST_DIR/default-sprint-windows-amd64.exe"
  else
    echo "Warning: default-sprint(.exe) not found in $tmp_dir"
  fi
  rm -rf "$tmp_dir"
}

build_runtime() {
  local arch="$1";
  local image="${RUNTIME_IMAGE:-yt-sprint-tool-runtime:debug-$arch}"
  local host_arch="$(uname -m)"
  local host_norm="$host_arch"
  case "$host_arch" in
    x86_64) host_norm="amd64" ;;
    aarch64|arm64) host_norm="arm64" ;;
  esac

  local load_args
  if [[ "$host_norm" == "$arch" ]]; then
    load_args=(--load)
  else
    local oci_path="$DIST_DIR/runtime-image-$arch.oci"
    echo "Host arch $host_norm differs from target $arch. Exporting OCI archive to $oci_path"
    load_args=(--output "type=oci,dest=$oci_path")
  fi

  echo "Building runtime image for linux/$arch (tag: $image)..."
  docker buildx build \
    --platform "linux/$arch" \
    -f Dockerfile \
    --build-arg FLAVOR=linux \
    --target runtime \
    "${load_args[@]}" \
    -t "$image" \
    .
}

case "$TARGET" in
  all)
    build_linux amd64
    build_linux arm64
    build_windows_amd64
    ;;
  runtime)
    build_runtime amd64
    ;;
  runtime-amd64)
    build_runtime amd64
    ;;
  runtime-arm64)
    build_runtime arm64
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

echo "Docker builds completed. See ./dist"
ls -la "$DIST_DIR" | sed -n '1,200p'
