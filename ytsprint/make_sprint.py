#!/usr/bin/env python3
"""
Creating sprints in YouTrack.

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
    make_sprint.py "Board Name" [2025.32]

If week is not specified, current week is used.
URL and token can be passed via environment variables YOUTRACK_URL and YOUTRACK_TOKEN.
"""

import argparse
import logging
import os
import sys
from typing import Optional

from ytsprint.lib_sprint import SprintService
from ytsprint.lib_yt_api import YouTrackAPI
from ytsprint.version import get_version_for_argparse

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for make-sprint CLI.

    Returns:
        argparse.Namespace: Parsed arguments including board, optional week,
        and YouTrack connection details (url, token).
    """
    parser = argparse.ArgumentParser(description="Creating sprint in YouTrack")
    parser.add_argument("board", help="Board name")
    parser.add_argument("week", nargs="?", help="Week in YYYY.WW format (default - current)")
    parser.add_argument(
        "--url", default=os.environ.get("YOUTRACK_URL"), help="YouTrack URL (or env YOUTRACK_URL)"
    )
    parser.add_argument(
        "--token", default=os.environ.get("YOUTRACK_TOKEN"), help="Bearer token (or env YOUTRACK_TOKEN)"
    )
    parser.add_argument(
        "--version", action="version", version=get_version_for_argparse("make-sprint"), help="Show version and exit"
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        default=os.environ.get("YTSPRINT_LOG_LEVEL", "INFO"),
        help=(
            "Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). "
            "If omitted, uses env YTSPRINT_LOG_LEVEL; default INFO."
        ),
    )
    return parser.parse_args()


def create_sprint(yt: YouTrackAPI, board_name: str, week_param: Optional[str]) -> None:
    """
    Create a sprint on a YouTrack Agile board for a specified (or current) week.

    Delegates to SprintService.create_sprint_for_week.

    Args:
        yt (YouTrackAPI): Initialized API client.
        board_name (str): Agile board name.
        week_param (str | None): Week in YYYY.WW format, or None for current.
    """
    SprintService(yt).create_sprint_for_week(board_name, week_param)


def main() -> None:
    """
    Entry point for make-sprint CLI.

    - Validates YouTrack URL and token.
    - Creates sprint for the requested or current week via SprintService.
    """
    args = parse_args()
    level = getattr(logging, str(args.log_level).upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    if not args.url or not args.token:
        logger.error(
            "Specify --url and --token or environment variables YOUTRACK_URL / YOUTRACK_TOKEN"
        )
        sys.exit(1)

    # Initialize API client
    yt = YouTrackAPI(args.url, args.token)

    # Create sprint
    create_sprint(yt, args.board, args.week)


if __name__ == "__main__":
    main()
