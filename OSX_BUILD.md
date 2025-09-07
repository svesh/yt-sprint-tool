# macOS: Cross-Build Setup (Colima + Docker Buildx)

This is a minimal, step-by-step guide to prepare macOS for Linux arm64/amd64 builds and to run containers for the required architecture.

## 1) Install Dependencies (one-time)

```bash
# Tools and updates
xcode-select --install 2>/dev/null || true
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" 2>/dev/null || true
brew update

# Core packages
brew install colima docker docker-buildx qemu

# Make the buildx plugin visible to the Docker CLI
mkdir -p ~/.docker/cli-plugins
ln -sfn "$(brew --prefix)/opt/docker-buildx/bin/docker-buildx" ~/.docker/cli-plugins/docker-buildx

# Reload shell environment
exec zsh
```

Verification:

```bash
docker version
docker buildx version
```

## 2) Two Colima Profiles

### 2.1 arm64 Profile (Apple Virtualization, fast I/O)

```bash
colima -p arm64 start \
  --arch aarch64 \
  --vm-type vz \
  --cpu 2 --memory 4 --disk 20 \
  --mount-type virtiofs \
  --mount "$HOME:w" \
  --binfmt=false
```

This creates a Docker context: `colima-arm64`.

### 2.2 amd64 Profile (QEMU, x86_64 emulation)

```bash
colima -p amd64 start \
  --arch x86_64 \
  --vm-type qemu \
  --cpu 2 --memory 4 --disk 20 \
  --mount-type 9p \
  --mount "$HOME:w" \
  --binfmt=false
```

This creates a Docker context: `colima-amd64`.

Verify contexts:

```bash
docker context ls | egrep 'colima-(arm64|amd64)'
docker --context colima-arm64 run --rm alpine uname -m         # arm64
docker --context colima-amd64 run --rm alpine uname -m         # x86_64
```

## 4) Buildx Cross Builder `cross` (arm64 + amd64)

> Reuse the auto-created contexts; no need for extra contexts/builders.

```bash
# arm64 node (default)
docker --context colima-arm64 buildx create \
  --name cross \
  --driver docker-container \
  --node arm64 \
  --use

# amd64 node (append)
docker --context colima-amd64 buildx create \
  --name cross \
  --append \
  --driver docker-container \
  --node amd64

# Warm up and verify platforms
docker buildx inspect --builder cross --bootstrap
# Platforms should include: linux/arm64 and linux/amd64
```

## 5) Publish a Multi-Arch Image to GitHub Container Registry (GHCR)

The script `scripts/push-multi-ghcr.sh` builds a multi-arch image (linux/arm64, linux/amd64) and publishes it to GHCR.

Preparation:

```bash
export GHCR_USER="<github_username>"
export GHCR_TOKEN="<ghcr_pat_with_write:packages>"
export IMAGE="ghcr.io/<owner>/<repo>"   # e.g., ghcr.io/svesh/yt-sprint-tool
export TAG="latest"                     # or any tag you need
```

Publish:

```bash
scripts/push-multi-ghcr.sh
```

Inspect the manifest:

```bash
docker buildx imagetools inspect "$IMAGE:$TAG"
```

## 6) Maintenance

```bash
# Stop / start a profile
colima -p arm64 stop && colima -p arm64 start
colima -p amd64 stop && colima -p amd64 start

# Remove a profile completely (VM data will be deleted)
colima -p arm64 delete -f
colima -p amd64 delete -f

# Recreate the cross builder
docker buildx rm cross 2>/dev/null || true
# then repeat section 4
```
