#!/usr/bin/env bash
set -euo pipefail

# Build runtime container images from binaries in dist/.
# Usage:
#   scripts/build-runtime.sh [--arch host|amd64|arm64] [--tag NAME] [--multi]
# Default arch: host (detected). Default tag: ytsprint-runtime

ARCH="host"
TAG_BASE="${RUNTIME_IMAGE:-ytsprint-runtime}"
MAKE_MULTI=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --arch)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --arch requires a value (host|amd64|arm64)" >&2
        exit 1
      fi
      case "$2" in
        host|amd64|arm64) ARCH="$2" ;;
        *) echo "Unknown arch: $2" >&2; exit 1 ;;
      esac
      shift 2
      ;;
    --tag)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --tag requires a value" >&2
        exit 1
      fi
      TAG_BASE="$2"
      shift 2
      ;;
    --multi)
      MAKE_MULTI=true
      shift
      ;;
    -h|--help)
      cat <<'USAGE'
Usage: scripts/build-runtime.sh [--arch host|amd64|arm64] [--tag NAME] [--multi]
Build runtime container images from binaries located in ./dist.
The default behavior builds an image for the host architecture with tag NAME:<arch>.
Use --multi to build an OCI archive containing amd64+arm64 images.
USAGE
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker is required." >&2
  exit 1
fi

if ! docker buildx version >/dev/null 2>&1; then
  echo "ERROR: docker buildx not found. Install or enable buildx." >&2
  exit 1
fi

resolve_arch() {
  local input="$1"
  case "$input" in
    host)
      local uname_m
      uname_m="$(uname -m)"
      case "$uname_m" in
        x86_64) echo "amd64" ;;
        aarch64|arm64) echo "arm64" ;;
        *) echo "Unsupported host arch: $uname_m" >&2; exit 1 ;;
      esac
      ;;
    amd64|arm64)
      echo "$input"
      ;;
    *)
      echo "Unsupported arch value: $input" >&2
      exit 1
      ;;
  esac
}

check_binary() {
  local arch="$1"
  local path="dist/ytsprint-linux-$arch"
  if [[ ! -f "$path" ]]; then
    echo "ERROR: $path not found. Build Linux binaries first." >&2
    exit 1
  fi
}

build_single() {
  local arch="$1"
  local image="${TAG_BASE}:${arch}"
  local platform="linux/$arch"
  local host_arch
  host_arch="$(resolve_arch host)"
  local output_opts

  if [[ "$host_arch" == "$arch" ]]; then
    output_opts=(--load)
    echo "Building runtime image $image for $platform (loaded into local Docker)..."
  else
    local oci_path="dist/ytsprint-runtime-${arch}.oci"
    echo "Host arch $host_arch differs from $arch. Exporting OCI archive to $oci_path"
    output_opts=(--output "type=oci,dest=$oci_path")
  fi

  docker buildx build \
    --platform "$platform" \
    -f Dockerfile \
    "${output_opts[@]}" \
    -t "$image" \
    .

  echo "Runtime image ready: $image"
}

build_multi() {
  local image="${TAG_BASE}:multi"
  local oci_path="dist/ytsprint-runtime-multi.oci"
  echo "Building multi-arch runtime image (amd64+arm64) -> $oci_path"
  docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -f Dockerfile \
    --output "type=oci,dest=$oci_path" \
    -t "$image" \
    .
  echo "Multi-arch OCI archive created: $oci_path"
  echo "Import with: docker buildx imagetools create --tag $image oci-archive:$oci_path"
}

if "$MAKE_MULTI"; then
  check_binary amd64
  check_binary arm64
  build_multi
else
  target_arch="$(resolve_arch "$ARCH")"
  check_binary "$target_arch"
  build_single "$target_arch"
fi
