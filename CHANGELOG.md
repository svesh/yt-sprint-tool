# Changelog

All notable changes to YT Sprint Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
