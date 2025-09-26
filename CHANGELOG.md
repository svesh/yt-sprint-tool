# Changelog

All notable changes to YT Sprint Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
