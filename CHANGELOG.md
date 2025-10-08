# Changelog

All notable changes to YT Sprint Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2025-10-08

### Fixed

- Docker runtime image now installs `ca-certificates` on Ubuntu 24.04, restoring TLS trust store at `/etc/ssl/certs/ca-certificates.crt` to fix HTTPS requests from `requests`.

### Changed

- Idempotent default sprint update: when switching a project's sprint field default, the tool removes only incorrect default values and adds only missing ones. If the current defaults already match the desired sprint, no changes are performed.

## [2.1.0] - 2025-09-27

### Added

- Test coverage for the unified CLI, sprint service helpers, and daemon runner to keep each module above 80% coverage.
- Native Windows build script (`scripts/windows-build.ps1`) used by CI and local developers for x64 and x86 executables.
- Documentation: restructured README with User/Developer guides, fixed relative links to CHANGELOG/AGENTS/OSX_BUILD, and added pointers to the latest release and GHCR image.

### Changed

- Replaced the `make-sprint` and `default-sprint` binaries with a single `ytsprint` executable that provides `--sync` (default) and `--create` modes.
- Updated build scripts, Docker packaging, and documentation to describe the unified CLI flow and artifacts.
- Local Docker helper (`scripts/build-linux-docker.sh`) targets Linux binaries, while `scripts/build-runtime.sh`
  assembles runtime images (single-arch or multi-arch OCI archives).
- Runtime Dockerfile copies binaries after dependency layers, exposes the Prometheus port, and uses cached
  system layers across architectures.
- Runtime Docker image builds consume pre-built binaries (dist locally, Linux artifacts in CI) and publish
  multi-architecture manifests in parallel Docker jobs.
- CI: enabled pip caching in Quality, Windows, and macOS jobs via actions/setup-python cache with `requirements.txt` as dependency path.
- CI: added explicit pip cache for Linux job using actions/cache on `~/.cache/pip`, keyed by `requirements.txt` and `scripts/internal/prepare-linux-deps.sh`.
- Build time: faster repeat builds across OSes; no changes to produced artifacts or runtime behaviour.

### Removed

- Deprecated modules `ytsprint/make_sprint.py`, `ytsprint/default_sprint.py`, and their dedicated CLI tests.
- Wine-based Windows build scripts and Docker support in favour of native Windows runners.

## [2.0.1] - 2025-09-26

### Added

- CI: multi-architecture Docker publishing job that builds from branches and release tags, pushes to GHCR, and applies OCI source metadata.

### Changed

- Docker runtime image now uses the `default-sprint` entrypoint, reads `YOUTRACK_URL`, `YOUTRACK_TOKEN`,
  `YOUTRACK_BOARD`, `YOUTRACK_PROJECT`, `YTSPRINT_CRON`, `YTSPRINT_FORWARD`, and `YTSPRINT_LOG_LEVEL`, and starts in
  daemon mode with the schedule and forward count sourced from environment defaults.
- default-sprint CLI resolves board, project, cron, and forward options from environment variables, aligning container behaviour with local execution.
- Documentation and runtime messages no longer use emoji glyphs; README describes the GHCR image and configuration.
- Tests now clear YouTrack credentials from the environment to prevent accidental access to live services during local runs.
- GitHub Actions workflow now builds and publishes multi-architecture images to GHCR for branches and release tags.
- build-with-docker helper can now produce the runtime image locally for debugging while keeping exported binaries clean.
- Daemon dependencies (apscheduler, prometheus_client) are now imported statically and installed with the package.

### Removed

- Legacy `scripts/push-multi-ghcr.sh` helper in favour of the GitHub Actions multi-arch publishing job.

## [2.0.0] - 2025-09-06

This release modernizes the codebase, build system, and CI. It introduces a package layout, adds reproducible builds across OSes, and consolidates quality tooling.

### Added

- default-sprint: `--forward N` (create N future sprints; default switches to actual)
- default-sprint: daemon `--daemon` + `--cron` (UTC); immediate first run
- Prometheus exporter: `ytsprint_cron_seconds`, `ytsprint_cron_status`
- Both CLIs: `--log-level` (or env `YTSPRINT_LOG_LEVEL`, default INFO)
- Development rules: added AGENTS.md with contribution guidelines
- New libraries: `ytsprint/lib_sprint.py` (SprintService), `ytsprint/lib_daemon.py` (DaemonRunner)

### Changed

- Documentation: README overhauled; project description expanded
- Build system: improvements to local builds and CI workflows
- Linters: reworked and consolidated compared to 1.0.0

## [1.0.0] - 2025-07-29

### Added

- CLI: make-sprint — create sprints for ISO weeks (YYYY.WW)
- CLI: default-sprint — sync project default sprint with board
- Utilities: ISO week/date helpers; YouTrack REST client
- Env support: `YOUTRACK_URL`, `YOUTRACK_TOKEN`
- Builds: Windows (.exe) and Linux (static)
- Quality: pytest with coverage, initial linting configuration
- Build tooling: Dockerfile and scripts (Linux, Wine/Windows)
- Windows: embedded version info for executables; argparse `--version`
- Docs & licensing: initial README and GPL-3.0 LICENSE
