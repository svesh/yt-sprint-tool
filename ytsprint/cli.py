#!/usr/bin/env python3
"""Unified command-line interface for YT Sprint Tool."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Optional, Tuple

from ytsprint.lib_daemon import DaemonRunner
from ytsprint.lib_sprint import SprintService
from ytsprint.lib_yt_api import YouTrackAPI
from ytsprint.version import get_version_for_argparse

logger = logging.getLogger(__name__)


def _read_env_int(name: str, default: int) -> Tuple[int, Optional[str]]:
    """Return integer value from environment or warning if parsing failed."""

    value = os.environ.get(name)
    if value in (None, ""):
        return default, None
    try:
        return int(value), None
    except ValueError:
        return default, f"Invalid {name} value '{value}'. Using {default}."


def parse_args() -> argparse.Namespace:
    """Configure and parse command-line arguments for the unified CLI."""

    forward_default, forward_warning = _read_env_int("YTSPRINT_FORWARD", 0)

    parser = argparse.ArgumentParser(description="YouTrack Sprint automation")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--sync",
        dest="mode",
        action="store_const",
        const="sync",
        help="Synchronize project default sprint (default mode)",
    )
    mode_group.add_argument(
        "--create",
        dest="mode",
        action="store_const",
        const="create",
        help="Create sprint only without touching project defaults",
    )
    parser.set_defaults(mode="sync")

    parser.add_argument(
        "--board",
        default=os.environ.get("YOUTRACK_BOARD", ""),
        help="Agile board name (or env YOUTRACK_BOARD)",
    )
    parser.add_argument(
        "--project",
        default=os.environ.get("YOUTRACK_PROJECT", ""),
        help="Project name for default sprint sync (or env YOUTRACK_PROJECT)",
    )
    parser.add_argument(
        "--field",
        default="Sprints",
        help="Project field name that stores sprints (default: Sprints)",
    )
    parser.add_argument("--week", help="ISO week in YYYY.WW format (default: current week)")
    parser.add_argument(
        "--forward",
        type=int,
        default=forward_default,
        help="How many future sprints to ensure exist (default: env YTSPRINT_FORWARD or 0)",
    )
    parser.add_argument("--daemon", action="store_true", help="Run sync in daemon mode with cron schedule")
    parser.add_argument(
        "--cron",
        default=os.environ.get("YTSPRINT_CRON", "0 8 * * 1"),
        help="Crontab expression for daemon schedule (default: env YTSPRINT_CRON or '0 8 * * 1')",
    )
    parser.add_argument(
        "--metrics-addr",
        default="0.0.0.0",
        help="Prometheus exporter bind address (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--metrics-port",
        type=int,
        default=9108,
        help="Prometheus exporter port (default: 9108)",
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("YOUTRACK_URL", ""),
        help="YouTrack URL (or env YOUTRACK_URL)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("YOUTRACK_TOKEN", ""),
        help="YouTrack bearer token (or env YOUTRACK_TOKEN)",
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        default=os.environ.get("YTSPRINT_LOG_LEVEL", "INFO"),
        help="Logging level (default: env YTSPRINT_LOG_LEVEL or INFO)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=get_version_for_argparse("ytsprint"),
        help="Show version and exit",
    )

    args = parser.parse_args()
    setattr(args, "env_forward_warning", forward_warning)
    return args


def _configure_logging(level_name: str) -> None:
    """Configure logging based on provided level name."""

    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _require(value: str, description: str, env_var: str) -> str:
    """Ensure required CLI argument or environment variable value is present."""

    normalized = value.strip()
    if not normalized:
        logger.error("Specify %s via option or environment variable %s", description, env_var)
        sys.exit(1)
    return normalized


def _init_service(url: str, token: str) -> SprintService:
    """Validate credentials and return initialized sprint service."""

    if not url or not token:
        logger.error("Specify --url and --token or environment variables YOUTRACK_URL / YOUTRACK_TOKEN")
        sys.exit(1)
    yt = YouTrackAPI(url, token)
    return SprintService(yt)


def main() -> None:
    """Entry point for unified ytsprint CLI."""

    args = parse_args()
    _configure_logging(str(args.log_level))

    if args.env_forward_warning:
        logger.warning(args.env_forward_warning)

    board = _require(args.board, "board name", "YOUTRACK_BOARD")
    service = _init_service(args.url, args.token)

    if args.mode == "create":
        if args.daemon:
            logger.error("--daemon is only supported in --sync mode")
            sys.exit(1)
        service.create_sprint_for_week(board, args.week)
        return

    project = _require(args.project, "project name", "YOUTRACK_PROJECT")
    field = args.field.strip() or "Sprints"
    forward = max(0, int(args.forward))

    def _run_once() -> None:
        service.run_sync_once(board, project, field, args.week, forward)

    if args.daemon:
        DaemonRunner(args.cron, args.metrics_addr, int(args.metrics_port)).start(_run_once)
        return

    _run_once()


if __name__ == "__main__":  # pragma: no cover
    main()
