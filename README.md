# YT Sprint Tool

> **⚠️ AI-Generated Content Notice**  
> This project and all its content (code, documentation, tests, build scripts)
> were fully generated using artificial intelligence tools. The project
> demonstrates modern AI-assisted development capabilities and serves as an
> example of human-AI collaboration in software engineering.

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/svesh/yt-sprint-tool/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![AI Assisted](https://img.shields.io/badge/AI-Assisted-purple?logo=openai)](https://github.com/svesh/yt-sprint-tool/)

Set of utilities for automating sprint management in YouTrack.

## Description

Two CLI utilities help manage weekly sprints in YouTrack with ISO calendar semantics:

- `make-sprint`: creates a sprint on a YouTrack Agile board for a given ISO week.
  The sprint name format is `YYYY.WW Sprint` (e.g., `2025.32 Sprint`).
  Dates span Monday–Friday (UTC), covering the full work week in milliseconds.
- `default-sprint`: synchronizes a project’s sprint field default (by default, `Sprints`)
  with the sprint of the requested week by resolving the value from the field’s bundle
  and applying it as the default.

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

## Download and Use

- Preferred: download binaries from Releases: <https://github.com/svesh/yt-sprint-tool/releases>
- Alternative (development): build locally — see the Development section.

### Usage

Set environment variables (recommended) or provide `--url` and `--token` flags explicitly:

```bash
export YOUTRACK_URL="https://youtrack.example.com"
export YOUTRACK_TOKEN="perm:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### make-sprint Utility

Create sprint for specified week on Agile board.

```bash
# Create sprint for current week
make-sprint "My Board"

# Create sprint for specific week
make-sprint "My Board" "2025.32"
```

### default-sprint Utility

Synchronize sprint values between board and project.

```bash
# Sync with default "Sprints" field
default-sprint "My Board" "My Project"

# Sync with custom field
default-sprint "My Board" "My Project" --field "Custom Field"

# For specific week
default-sprint "My Board" "My Project" --week "2025.32"

# Ensure future sprints (create next N weeks)
default-sprint "My Board" "My Project" --forward 2

# Run as a daemon (UTC) every Monday 08:00, with Prometheus metrics
default-sprint "My Board" "My Project" \
  --daemon \
  --cron "0 8 * * 1" \
  --metrics-addr 0.0.0.0 \
  --metrics-port 9108
```

## Parameters

### Common Parameters

- `--url` - YouTrack server URL (or env `YOUTRACK_URL`)
- `--token` - Bearer token for API (or env `YOUTRACK_TOKEN`)

### make_sprint.py Parameters

- `board` - Agile board name (positional argument)
- `week` - Week in YYYY.WW format (optional positional argument)
- `--log-level` - Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). If omitted, uses env `YTSPRINT_LOG_LEVEL`; default `INFO`.

### default_sprint.py Parameters

- `board` - Agile board name (positional argument)
- `project` - Project name (positional argument)
- `--field` - Project field name (default "Sprints")
- `--week` - Week in YYYY.WW format (default - current)
- `--forward` - How many future sprints to ensure exist (default: 0). Default value is always switched to the current sprint.
- `--daemon` - Run as background daemon with cron schedule (UTC)
- `--cron` - Crontab string for schedule (default: `0 8 * * 1`)
- `--metrics-addr` - Prometheus exporter bind address (default: `0.0.0.0`)
- `--metrics-port` - Prometheus exporter port (default: `9108`)
- `--log-level` - Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). If omitted, uses env `YTSPRINT_LOG_LEVEL`; default `INFO`.

Prometheus metrics exposed at `http://<metrics-addr>:<metrics-port>/metrics`:

- `ytsprint_cron_seconds`: seconds since last cron run (NaN until first run)
- `ytsprint_cron_status`: last run status (`1` on success, `0` on failure)

## Development

See AGENTS.md for contribution rules (patch-based edits; keep all checks green).

### Dependencies

- Python 3.12+
- Docker (recommended for local builds)
- YouTrack URL and token

### Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run All Checks

```bash
bash scripts/linters.sh
```

### Local Build

Preferred: Docker wrapper (stable, reproducible)

```bash
bash scripts/build-with-docker.sh            # all
bash scripts/build-with-docker.sh linux-amd64
bash scripts/build-with-docker.sh linux-arm64
bash scripts/build-with-docker.sh windows-amd64
```

Native (for development):

```bash
# Linux (static)
bash scripts/linux-install-deps.sh
bash scripts/linux-build.sh

# Windows (Wine on Linux)
bash scripts/wine-install-deps.sh
bash scripts/wine-build.sh

# macOS (native on host arch)
bash scripts/macos-build.sh
```

On macOS, see local Docker setup and notes in [OSX_BUILD.md](OSX_BUILD.md).

### Package Structure

- `ytsprint/lib_date_utils.py` — utilities for ISO weeks
- `ytsprint/lib_yt_api.py` — YouTrack REST API client
- `ytsprint/lib_sprint.py` — sprint service (ensure/create, defaults, forward, one‑off sync)
- `ytsprint/lib_daemon.py` — daemon runner (cron, Prometheus metrics)
- `ytsprint/make_sprint.py` — CLI entry (make‑sprint)
- `ytsprint/default_sprint.py` — CLI entry (default‑sprint)

### Using Binaries (from dist/)

```bash
# Linux
./dist/make-sprint-linux "My Board" "2025.32"
./dist/default-sprint-linux "My Board" "My Project" --field "Sprints"

# Windows
./dist/make-sprint-windows-amd64.exe "My Board" "2025.32"
./dist/default-sprint-windows-amd64.exe "My Board" "My Project" --field "Sprints"
```

## Authors and Contributors

### 👨‍💻 Primary Author

**Sergei Sveshnikov** - concept development, architecture, testing

- Email: [svesh87@gmail.com](mailto:svesh87@gmail.com)
- GitHub: [@svesh](https://github.com/svesh)

### 🤖 AI Co-authors

- v1.0.0 — **GitHub Copilot (Claude 4 Sonnet)**: initial scaffolding, early tests, documentation, and build system ideas
- v2.0.0 — **OpenAI Codex CLI (AI assistant)**: package refactor, logging improvements, test relocation and coverage, CI workflows, build scripts, and documentation updates

### 🤝 Collaborative Development

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
