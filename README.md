# YT Sprint Tool

> **AI-Generated Content Notice**  
> This project and all its content (code, documentation, tests, build scripts)
> were fully generated using artificial intelligence tools. The project
> demonstrates modern AI-assisted development capabilities and serves as an
> example of human-AI collaboration in software engineering.

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/svesh/yt-sprint-tool/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![AI Assisted](https://img.shields.io/badge/AI-Assisted-purple?logo=openai)](https://github.com/svesh/yt-sprint-tool/)

Set of utilities for automating sprint management in YouTrack.

Helpful references:

- See CHANGELOG: [CHANGELOG.md](CHANGELOG.md)
- Agent rules: [AGENTS.md](AGENTS.md)
- macOS notes: [OSX_BUILD.md](OSX_BUILD.md)

## Overview

The unified `ytsprint` CLI manages ISO-week sprints in YouTrack and exposes two
execution modes:

- **Sync** (`--sync`, default) – ensures the sprint for the requested week
  exists on the board, updates the project default field, can provision future
  weeks, and supports cron-driven daemon execution.
- **Create** (`--create`) – guarantees that the `YYYY.WW Sprint` exists on the
  board without modifying project settings.

### Features

- ISO week support (Monday–Friday)
- Automatic current week detection
- Positional arguments for ease of use
- Comprehensive error handling and logging
- Docker-ready architecture for easy deployment
- Standalone binaries for independent distribution

### Requirements (runtime)

- YouTrack server URL
- YouTrack REST API token
- Access to YouTrack server

## User Guide

### Download

- Recommended: download binaries from the latest release:
  <https://github.com/svesh/yt-sprint-tool/releases/latest>
  Typical assets: `ytsprint-linux-amd64`, `ytsprint-linux-arm64`,
  `ytsprint-windows-x64.exe`, `ytsprint-windows-x86.exe`, `ytsprint-macos-<arch>`.
- For development, build locally — see the Developer Guide.

### Usage

Set environment variables (recommended) or provide `--url` and `--token` flags explicitly:

```bash
export YOUTRACK_URL="https://youtrack.example.com"
export YOUTRACK_TOKEN="perm:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### CLI Examples

```bash
# Create a sprint for the current week (create mode)
ytsprint --create --board "My Board"

# Create a sprint for a specific week
ytsprint --create --board "My Board" --week "2025.32"

# Synchronize project defaults (sync mode)
ytsprint --board "My Board" --project "My Project"

# Sync with a custom field and ensure two future weeks
ytsprint --board "My Board" --project "My Project" --field "Custom Field" --forward 2

# Sync for a specific week
ytsprint --board "My Board" --project "My Project" --week "2025.32"

# Ensure future weeks while syncing
ytsprint --board "My Board" --project "My Project" --forward 2

# Run as a daemon with Prometheus metrics
ytsprint --board "My Board" --project "My Project" \
  --daemon \
  --cron "0 8 * * 1" \
  --metrics-addr 0.0.0.0 \
  --metrics-port 9108
```

### Parameters

### Common options

- `--board` – Agile board name (or env `YOUTRACK_BOARD`)
- `--week` – ISO week in `YYYY.WW` format (defaults to the current week)
- `--url` – YouTrack URL (or env `YOUTRACK_URL`)
- `--token` – YouTrack REST token (or env `YOUTRACK_TOKEN`)
- `--log-level` – logging verbosity (or env `YTSPRINT_LOG_LEVEL`, default `INFO`)

### `--create` mode

- Uses only board, week, URL, token, and log level options
- Mutually exclusive with `--daemon`

### `--sync` mode

- `--project` – project name (or env `YOUTRACK_PROJECT`)
- `--field` – project field name (default `Sprints`)
- `--forward` – number of future sprints to create/ensure (or env `YTSPRINT_FORWARD`)
- `--daemon` – run continuously on a cron schedule
- `--cron` – cron expression (or env `YTSPRINT_CRON`, default `0 8 * * 1`)
- `--metrics-addr`, `--metrics-port` – Prometheus exporter binding

Prometheus metrics exposed at `http://<metrics-addr>:<metrics-port>/metrics`:

- `ytsprint_cron_seconds`: seconds since last cron run (NaN until first run)
- `ytsprint_cron_status`: last run status (`1` on success, `0` on failure)

### Docker Runtime Image

Multi-architecture images (linux/amd64 and linux/arm64) are published to GitHub Container Registry at `ghcr.io/svesh/yt-sprint-tool`.
Browse tags and metadata: <https://github.com/users/svesh/packages/container/package/yt-sprint-tool>

Environment variables recognised by the runtime image:

- `YOUTRACK_URL` – YouTrack base URL (required)
- `YOUTRACK_TOKEN` – YouTrack permanent token (required)
- `YOUTRACK_BOARD` – default board name used when positional arguments are omitted
- `YOUTRACK_PROJECT` – default project name used when positional arguments are omitted
- `YTSPRINT_CRON` – cron expression for daemon mode (default: `0 8 * * 1`)
- `YTSPRINT_FORWARD` – number of future sprints to ensure (default inside the container: `1`)
- `YTSPRINT_LOG_LEVEL` – logging verbosity (`INFO`, `DEBUG`, etc.; default: `INFO`)

The container entrypoint is the `ytsprint` binary.
By default it runs sync mode in daemon configuration using environment-provided settings.
Pass the board and project via options or override other parameters on launch:

```bash
docker run --rm \
  -e YOUTRACK_URL="https://youtrack.example.com" \
  -e YOUTRACK_TOKEN="perm:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  ghcr.io/svesh/yt-sprint-tool --board "My Board" --project "My Project" --daemon
```

Docker replaces the default command when explicit arguments are supplied, so the
container relies on environment defaults for the cron schedule and forward count
unless you override them with explicit flags. If you omit `--board` and
`--project`, set `YOUTRACK_BOARD` and `YOUTRACK_PROJECT` so the entrypoint can
infer them automatically.

Customise scheduling or log verbosity by overriding the corresponding environment variables (for example, `-e YTSPRINT_CRON="0 */2 * * 1-5"`).

## Developer Guide

See [AGENTS.md](AGENTS.md) for contribution rules (patch-based edits; keep all checks green).

### Dependencies

- Python 3.12+
- Docker (recommended for local builds)
- YouTrack URL and token

### Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Install in editable mode for development
pip install -e .
# Linux only: install patchelf and staticx toolchain
sudo apt-get update && sudo apt-get install -y patchelf
pip install "scons>=4.7"
pip install --no-build-isolation staticx==0.14.1
```

### Run All Checks

```bash
bash scripts/linters.sh
```

### Local Build

#### Linux (native)

```bash
# Builds dist/ytsprint-linux-<arch>
bash scripts/linux-build.sh
```

#### Linux (Docker)

```bash
bash scripts/build-linux-docker.sh            # amd64 + arm64 sequentially
bash scripts/build-linux-docker.sh --arch amd64
bash scripts/build-linux-docker.sh --arch arm64
```

#### Runtime Container

```bash
# Requires binaries in ./dist (see Linux build steps)
bash scripts/build-runtime.sh                  # host architecture (amd64 or arm64)
bash scripts/build-runtime.sh --arch amd64     # build linux/amd64 image
bash scripts/build-runtime.sh --arch arm64     # build linux/arm64 image
bash scripts/build-runtime.sh --multi          # create dist/ytsprint-runtime-multi.oci (amd64+arm64)
# Import the multi-arch archive into your registry (example):
# docker buildx imagetools create --tag ghcr.io/svesh/yt-sprint-tool:local \
#   oci-archive:dist/ytsprint-runtime-multi.oci
```

#### Windows (native PowerShell)

```powershell
pwsh -File scripts/windows-build.ps1          # emits dist/ytsprint-windows-x64.exe or -x86.exe (matches Python bitness)
# Note: the architecture of the output equals the architecture of the active Python
# (64-bit Python -> x64 exe; 32-bit Python -> x86 exe).
```

#### macOS (native)

```bash
bash scripts/macos-build.sh                    # emits dist/ytsprint-macos-<arch> (arch = host, e.g., arm64 on Apple Silicon)
```

On macOS, see local Docker setup and notes in [OSX_BUILD.md](OSX_BUILD.md).

### Architecture and Modules

- `ytsprint/cli.py` — unified CLI entry point; parses args for `--sync` and `--create`, routes to services.
- `ytsprint/lib_sprint.py` — sprint service: ISO week calculation, board/project interactions, forward sprint provisioning.
- `ytsprint/lib_yt_api.py` — typed wrapper over YouTrack REST API (boards, projects, sprints, bundles), with helpers for default fields.
- `ytsprint/lib_date_utils.py` — ISO week/date utilities (parse/format `YYYY.WW`, date ranges, current week).
- `ytsprint/lib_daemon.py` — APScheduler-based cron runner with Prometheus metrics exporter (seconds/status gauges).

### Distribution Artifacts (dist/)

File name templates placed into `dist/` after builds:
- Linux: `ytsprint-linux-amd64`, `ytsprint-linux-arm64`
- Windows: `ytsprint-windows-x64.exe`, `ytsprint-windows-x86.exe`
- macOS: `ytsprint-macos-<arch>` (e.g., `arm64` or `x86_64`)

### Script Reference

- `scripts/linux-build.sh` — builds Linux binary via PyInstaller + staticx using the active Python environment.
- `scripts/build-linux-docker.sh` — builds Linux binaries via Docker (`Dockerfile.build`).
- `scripts/build-runtime.sh` — assembles the runtime container image (single architecture or multi-arch OCI archive).
- `scripts/windows-build.ps1` — builds Windows executable (auto-detects Python architecture).
- `scripts/macos-build.sh` — builds macOS artifact on the host architecture.
- `scripts/linters.sh` — runs linting and test suites.

#### Internal Scripts

- `scripts/internal/prepare-linux-deps.sh` — installs system packages for Linux builds (used in CI and Docker builder stages).

### Linters and Rules

- Aggregate command: `scripts/linters.sh` runs pylint, pyright, isort (check), markdown lint, yamllint, and pytest with coverage.
- Configurations:
  - Pylint/Pyright/pytest: [pyproject.toml](pyproject.toml)
  - Markdown: [.pymarkdownlnt.json](.pymarkdownlnt.json)
  - YAML: [.yamllint.yaml](.yamllint.yaml)

## Authors and Contributors

### Primary Author

**Sergei Sveshnikov** - concept development, architecture, testing

- Email: [svesh87@gmail.com](mailto:svesh87@gmail.com)
- GitHub: [@svesh](https://github.com/svesh)

### AI Co-authors

- v1.0.0 — **GitHub Copilot (Claude 4 Sonnet)**: initial scaffolding, early tests, documentation, and build system ideas
- v2.0.X — **OpenAI Codex CLI (AI assistant)**: package refactor, logging improvements, test relocation and coverage, CI workflows, build scripts, and documentation updates

### Collaborative Development

This project demonstrates effective collaboration between human expertise and artificial intelligence capabilities. The AI assistant participated in:

- Designing modular architecture
- Writing core code and utilities
- Creating Docker + Wine + staticx build system
- Developing comprehensive testing (pytest)
- Setting up linting and code quality
- Creating documentation and changelog
- Performance optimization and cross-platform compatibility

*This development approach represents a modern model of collaborative programming, where AI acts as a full team member in the development process.*

## License

This project is distributed under the **GNU General Public License v3.0** (GPL-3.0).

Full license text is available in the [`LICENSE`](LICENSE) file.

For questions about licensing or commercial use, contact: [svesh87@gmail.com](mailto:svesh87@gmail.com)

---

© 2025 [Sergei Sveshnikov](mailto:svesh87@gmail.com) | [GitHub Project](https://github.com/svesh/yt-sprint-tool/)
