#!/usr/bin/env python3
"""
Synchronizing default sprint values between board and project in YouTrack.

Copyright (C) 2025 Sergei Sveshnikov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Usage:
    default_sprint.py "Board Name" "Project Name" [--field "Field Name"] [--week 2025.32] [--forward N]
    default_sprint.py "Board Name" "Project Name" --daemon --cron "0 8 * * 1" [--metrics-addr 0.0.0.0] [--metrics-port 9108]

Simplified version using methods from lib_yt_api and lib_date_utils libraries.
"""

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
    """Parse an integer from environment variable with graceful fallback."""

    value = os.environ.get(name)
    if value is None or value == "":
        return default, None
    try:
        return int(value), None
    except ValueError:
        return default, f"Invalid {name} value '{value}'. Using {default}."


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for default-sprint CLI.

    Args:
        None

    Returns:
        argparse.Namespace: Parsed arguments including board, project, field,
        week, forward count, daemon flags (cron, metrics-addr, metrics-port),
        and YouTrack connection details (url, token).
    """
    forward_default, forward_warning = _read_env_int("YTSPRINT_FORWARD", 0)

    parser = argparse.ArgumentParser(description="Sprint synchronization between board and project")
    parser.add_argument(
        "board",
        nargs="?",
        default=os.environ.get("YOUTRACK_BOARD", ""),
        help="Board name (or env YOUTRACK_BOARD)",
    )
    parser.add_argument(
        "project",
        nargs="?",
        default=os.environ.get("YOUTRACK_PROJECT", ""),
        help="Project name (or env YOUTRACK_PROJECT)",
    )
    parser.add_argument("--field", default="Sprints", help="Field name (default: Sprints)")
    parser.add_argument("--week", help="Week in YYYY.WW format (default - current)")
    parser.add_argument(
        "--forward",
        type=int,
        default=forward_default,
        help=(
            "How many future sprints to ensure exist. "
            "Default: env YTSPRINT_FORWARD or 0. "
            "Always switches project default to the actual sprint."
        ),
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as a daemon with cron schedule (UTC)",
    )
    parser.add_argument(
        "--cron",
        default=os.environ.get("YTSPRINT_CRON", "0 8 * * 1"),
        help="Crontab string for daemon schedule (UTC). Default: env YTSPRINT_CRON or '0 8 * * 1'",
    )
    parser.add_argument(
        "--metrics-addr",
        default="0.0.0.0",
        help="Prometheus exporter address (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--metrics-port",
        type=int,
        default=9108,
        help="Prometheus exporter port (default: 9108)",
    )
    parser.add_argument("--url", default=os.environ.get("YOUTRACK_URL", ""), help="YouTrack URL (or env YOUTRACK_URL)")
    parser.add_argument("--token", default=os.environ.get("YOUTRACK_TOKEN", ""), help="Bearer token (or env YOUTRACK_TOKEN)")
    parser.add_argument(
        "--version",
        action="version",
        version=get_version_for_argparse("default-sprint"),
        help="Show version and exit",
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        default=os.environ.get("YTSPRINT_LOG_LEVEL", "INFO"),
        help=(
            "Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). "
            "If omitted, uses env YTSPRINT_LOG_LEVEL or INFO."
        ),
    )
    parser.set_defaults(env_forward_warning=forward_warning, env_forward_default=forward_default)
    return parser.parse_args()


def _start_daemon(yt: YouTrackAPI, args: argparse.Namespace) -> None:
    """
    Start daemon using DaemonRunner with a job that performs a single sync.

    Builds a closure that invokes SprintService.run_sync_once with parameters
    from CLI, then runs it on the configured cron schedule in UTC.

    Args:
        yt (YouTrackAPI): Initialized API client.
        args (argparse.Namespace): Parsed CLI arguments (board, project, field,
            week, forward, cron, metrics-addr, metrics-port).

    Returns:
        None
    """
    def _job() -> None:
        SprintService(yt).run_sync_once(args.board, args.project, args.field, args.week, args.forward)
    DaemonRunner(str(args.cron), str(args.metrics_addr), int(args.metrics_port)).start(_job)


def main() -> None:
    """
    Entry point for default-sprint CLI.

    - Validates YouTrack URL and token
    - In single-run mode executes SprintService.run_sync_once
    - In daemon mode schedules the sync job via DaemonRunner

    Args:
        None

    Returns:
        None
    """
    args = parse_args()
    raw_log_level = args.log_level

    # Configure logging with CLI/env-provided level
    level = getattr(logging, str(raw_log_level).upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    forward_warning = getattr(args, "env_forward_warning", None)
    forward_default = getattr(args, "env_forward_default", args.forward)
    if forward_warning and args.forward == forward_default:
        logger.warning(forward_warning)

    if not args.board or not args.project:
        logger.error("Specify board and project or set YOUTRACK_BOARD / YOUTRACK_PROJECT")
        sys.exit(1)

    if not args.url or not args.token:
        logger.error(
            "Specify --url and --token or environment variables YOUTRACK_URL / YOUTRACK_TOKEN"
        )
        sys.exit(1)

    # API initialization
    yt = YouTrackAPI(args.url, args.token)

    if args.daemon:
        _start_daemon(yt, args)
        return

    SprintService(yt).run_sync_once(args.board, args.project, args.field, args.week, args.forward)
    logger.info("Synchronization completed")


if __name__ == "__main__":
    main()
