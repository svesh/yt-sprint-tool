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
    default_sprint.py "Board Name" "Project Name" [--field "Field Name"] [--week 2025.32]

Simplified version using methods from lib_yt_api and lib_date_utils libraries.
"""

import argparse
import logging
import os
import sys
from typing import Tuple

from ytsprint.lib_date_utils import DateUtils
from ytsprint.lib_yt_api import YouTrackAPI
from ytsprint.version import get_version_for_argparse


def parse_args() -> argparse.Namespace:
    """Command line argument parsing."""
    parser = argparse.ArgumentParser(description="Sprint synchronization between board and project")
    parser.add_argument("board", help="Board name")
    parser.add_argument("project", help="Project name")
    parser.add_argument("--field", default="Sprints", help="Field name (default: Sprints)")
    parser.add_argument("--week", help="Week in YYYY.WW format (default - current)")
    parser.add_argument(
        "--url", default=os.environ.get("YOUTRACK_URL"), help="YouTrack URL (or env YOUTRACK_URL)"
    )
    parser.add_argument(
        "--token", default=os.environ.get("YOUTRACK_TOKEN"), help="Bearer token (or env YOUTRACK_TOKEN)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=get_version_for_argparse("default-sprint"),
        help="Show version and exit",
    )
    return parser.parse_args()


def setup_sprint(yt: YouTrackAPI, board_name: str, sprint_name: str, start_ms: int, finish_ms: int) -> None:
    """Setting up sprint on board."""
    # Search for board
    board_id = yt.find_board_id(board_name)
    if not board_id:
        print(f"❌ Board '{board_name}' not found")
        sys.exit(1)
    print(f"✅ BOARD_ID = {board_id}")

    # Create/find sprint on board
    sprint_id = yt.find_sprint_id(board_id, sprint_name)
    if not sprint_id:
        print(f"🔨 Creating sprint '{sprint_name}'")
        sprint_data = {"name": sprint_name, "start_ms": start_ms, "finish_ms": finish_ms}
        sprint = yt.create_sprint(board_id, sprint_data)
        sprint_id = sprint.get("id")
    else:
        print(f"✅ Sprint '{sprint_name}' already exists")
    print(f"✅ SPRINT_ID = {sprint_id}")


def setup_project_field(yt: YouTrackAPI, project_name: str, field_name: str, sprint_name: str) -> Tuple[str, str]:
    """Setting up project field."""
    print(f"🎯 Setting default value for field '{field_name}': {sprint_name}")

    # Search for project
    project_id = yt.find_project_id(project_name)
    if not project_id:
        print(f"❌ Project '{project_name}' not found")
        sys.exit(1)
    print(f"✅ PROJECT_ID = {project_id}")

    # Get project fields with bundle values
    fields = yt.get_project_fields(project_id)

    # Search for needed field
    project_field = None
    for field_data in fields:
        field = field_data.get("field", {})
        if field.get("name") == field_name:
            project_field = field_data
            break

    if not project_field:
        print(f"❌ Field '{field_name}' not found in project '{project_name}'")
        sys.exit(1)

    project_field_id = project_field["id"]
    bundle = project_field.get("bundle", {})
    values = bundle.get("values", [])

    print(f"✅ PROJECT_FIELD_ID = {project_field_id}")

    # Search for value in bundle by sprint name
    value_id = yt.find_bundle_value_by_name(values, sprint_name)
    if not value_id:
        print(
            f"❌ Value '{sprint_name}' not found in bundle for field '{field_name}' in project '{project_name}'"
        )
        sys.exit(1)
    print(f"✅ Bundle value matched: {sprint_name} -> {value_id}")

    # Update default values
    print("🎯 Updating default values")
    yt.update_field_default_values(project_id, project_field_id, [value_id])

    return project_id, project_field_id


def verify_setup(yt: YouTrackAPI, project_id: str, field_id: str) -> None:
    """Verify final setup."""
    print("🔍 Verifying final setup...")
    result = yt.get_field_defaults(project_id, field_id)
    field_name = result.get("field", {}).get("name", "N/A")
    defaults = result.get("defaultValues", [])

    print(f"✅ Field: {field_name}")
    if defaults:
        for default in defaults:
            print(f"✅ Default value: {default.get('name')} (id: {default.get('id')})")
    else:
        print("⚠️ No default values")


def main() -> None:
    """Main function."""
    # Enable informative logging by default
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    args = parse_args()

    if not args.url or not args.token:
        print(
            "❌ Specify --url and --token or environment variables YOUTRACK_URL / YOUTRACK_TOKEN",
            file=sys.stderr,
        )
        sys.exit(1)

    # API initialization
    yt = YouTrackAPI(args.url, args.token)

    # Process week parameter
    result = DateUtils.process_week_parameter(args.week)
    year, week, sprint_name, monday, friday, start_ms, finish_ms = result

    print(f"📅 Week: {year}.{week:02d} ({monday} - {friday})")
    print(f"🏃 Sprint: {sprint_name}")

    # Sprint setup
    setup_sprint(yt, args.board, sprint_name, start_ms, finish_ms)

    # Project field setup
    project_id, field_id = setup_project_field(yt, args.project, args.field, sprint_name)

    # Verification
    verify_setup(yt, project_id, field_id)

    print("🎉 Synchronization completed!")


if __name__ == "__main__":
    main()
