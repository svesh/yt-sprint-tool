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

from ytsprint.lib_date_utils import DateUtils
from ytsprint.lib_yt_api import YouTrackAPI
from ytsprint.version import get_version_for_argparse


def parse_args() -> argparse.Namespace:
    """Command line argument parsing."""
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
    return parser.parse_args()


def create_sprint(yt: YouTrackAPI, board_name: str, week_param: Optional[str]) -> None:
    """Creating sprint on board."""
    # Process week parameter
    year, week, sprint_name, monday, friday, start_ms, finish_ms = DateUtils.process_week_parameter(week_param)

    print(f"📅 Week: {year}.{week:02d} ({monday} - {friday})")
    print(f"🏃 Sprint: {sprint_name}")

    # Search for board
    board_id = yt.find_board_id(board_name)
    if not board_id:
        print(f"❌ Board '{board_name}' not found")
        sys.exit(1)
    print(f"✅ BOARD_ID = {board_id}")

    # Check if sprint exists
    if yt.sprint_exists(board_id, sprint_name):
        print(f"⚠️ Sprint '{sprint_name}' already exists")
        sys.exit(0)

    # Create sprint
    sprint_data = {"name": sprint_name, "start_ms": start_ms, "finish_ms": finish_ms}
    sprint = yt.create_sprint(board_id, sprint_data)
    print(f"✅ Created sprint: {sprint.get('name')} (ID: {sprint.get('id')})")
    print("🎉 Done!")


def main() -> None:
    """Main function for creating sprint."""
    # Enable informative logging by default
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    args = parse_args()

    if not args.url or not args.token:
        print(
            "❌ Specify --url and --token or environment variables YOUTRACK_URL / YOUTRACK_TOKEN",
            file=sys.stderr,
        )
        sys.exit(1)

    # Initialize API client
    yt = YouTrackAPI(args.url, args.token)

    # Create sprint
    create_sprint(yt, args.board, args.week)


if __name__ == "__main__":
    main()
