#!/usr/bin/env python3
"""
Sprint-related operations for YT Sprint Tool.

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

Provides class-based API via SprintService for:
- ensuring a sprint exists on a board
- switching project default sprint
- verifying defaults
- creating forward sprints
- running a one-off synchronization
- creating a sprint for a given week
"""

from __future__ import annotations

import datetime as dt
import logging
import sys
from typing import Optional, Tuple

from ytsprint.lib_date_utils import DateUtils
from ytsprint.lib_yt_api import YouTrackAPI

logger = logging.getLogger(__name__)


class SprintService:
    """
    Service class encapsulating sprint-related operations.

    Args:
        yt (YouTrackAPI): Initialized YouTrack API client.
    """

    def __init__(self, yt: YouTrackAPI) -> None:
        """
        Initialize service with API client.

        Args:
            yt (YouTrackAPI): Initialized YouTrack API client.
        """
        self.yt = yt

    def ensure_sprint_on_board(self, board_name: str, sprint_name: str, start_ms: int, finish_ms: int) -> None:
        """
        Ensure that a sprint exists on a board; create it if missing.

        Args:
            board_name (str): Agile board name.
            sprint_name (str): Sprint name to ensure.
            start_ms (int): Sprint start in UTC milliseconds.
            finish_ms (int): Sprint end in UTC milliseconds.

        Raises:
            SystemExit: If board is not found.
        """
        board_id = self.yt.find_board_id(board_name)
        if not board_id:
            logger.error("❌ Board '%s' not found", board_name)
            raise SystemExit(1)
        logger.info("✅ BOARD_ID = %s", board_id)

        sprint_id = self.yt.find_sprint_id(board_id, sprint_name)
        if not sprint_id:
            logger.info("🔨 Creating sprint '%s'", sprint_name)
            sprint_data = {"name": sprint_name, "start_ms": start_ms, "finish_ms": finish_ms}
            sprint = self.yt.create_sprint(board_id, sprint_data)
            sprint_id = sprint.get("id")
        else:
            logger.info("✅ Sprint '%s' already exists", sprint_name)
        logger.info("✅ SPRINT_ID = %s", sprint_id)

    def set_project_default_sprint(self, project_name: str, field_name: str, sprint_name: str) -> Tuple[str, str]:
        """
        Switch project's sprint field default to the given sprint name.

        Args:
            project_name (str): Project name.
            field_name (str): Sprint field name.
            sprint_name (str): Sprint name (must exist in the field bundle).

        Returns:
            tuple: (project_id, project_field_id)

        Raises:
            SystemExit: If project, field or value are not found.
        """
        logger.info("🎯 Setting default value for field '%s': %s", field_name, sprint_name)

        project_id = self.yt.find_project_id(project_name)
        if not project_id:
            logger.error("❌ Project '%s' not found", project_name)
            raise SystemExit(1)
        logger.info("✅ PROJECT_ID = %s", project_id)

        fields = self.yt.get_project_fields(project_id)
        project_field = None
        for field_data in fields:
            field = field_data.get("field", {})
            if field.get("name") == field_name:
                project_field = field_data
                break

        if not project_field:
            logger.error("❌ Field '%s' not found in project '%s'", field_name, project_name)
            raise SystemExit(1)

        project_field_id = project_field["id"]
        bundle = project_field.get("bundle", {})
        values = bundle.get("values", [])

        logger.info("✅ PROJECT_FIELD_ID = %s", project_field_id)

        value_id = self.yt.find_bundle_value_by_name(values, sprint_name)
        if not value_id:
            logger.error(
                "❌ Value '%s' not found in bundle for field '%s' in project '%s'",
                sprint_name,
                field_name,
                project_name,
            )
            raise SystemExit(1)
        logger.info("✅ Bundle value matched: %s -> %s", sprint_name, value_id)

        logger.info("🎯 Updating default values")
        self.yt.update_field_default_values(project_id, project_field_id, [value_id])
        return project_id, project_field_id

    def verify_project_default(self, project_id: str, field_id: str) -> None:
        """
        Print verification of current default values for the field.

        Args:
            project_id (str): Project ID.
            field_id (str): Project field ID.
        """
        logger.info("🔍 Verifying final setup...")
        result = self.yt.get_field_defaults(project_id, field_id)
        field_name = result.get("field", {}).get("name", "N/A")
        defaults = result.get("defaultValues", [])

        logger.info("✅ Field: %s", field_name)
        if defaults:
            for default in defaults:
                logger.info("✅ Default value: %s (id: %s)", default.get("name"), default.get("id"))
        else:
            logger.warning("⚠️ No default values")

    def ensure_future_sprints(self, board_name: str, base_year: int, base_week: int, count: int) -> None:
        """
        Create up to `count` future ISO-week sprints on the board if missing.

        Args:
            board_name (str): Agile board name.
            base_year (int): Base ISO year.
            base_week (int): Base ISO week number.
            count (int): How many future sprints to ensure.

        Raises:
            SystemExit: If board is not found.
        """
        if count <= 0:
            return

        board_id = self.yt.find_board_id(board_name)
        if not board_id:
            logger.error("❌ Board '%s' not found", board_name)
            raise SystemExit(1)

        base_monday = dt.date.fromisocalendar(base_year, base_week, 1)
        for i in range(1, count + 1):
            next_monday = base_monday + dt.timedelta(days=7 * i)
            iso_year, iso_week, _ = next_monday.isocalendar()
            sprint_name = DateUtils.format_sprint_name(iso_year, iso_week)
            _, _, start_ms, finish_ms = DateUtils.iso_week_range_utc(iso_year, iso_week)

            if self.yt.sprint_exists(board_id, sprint_name):
                logger.info("✅ Future sprint exists: %s", sprint_name)
                continue
            logger.info("🔨 Creating future sprint: %s", sprint_name)
            self.yt.create_sprint(board_id, {"name": sprint_name, "start_ms": start_ms, "finish_ms": finish_ms})

    def run_sync_once(self, board: str, project: str, field: str, week: Optional[str], forward: int) -> None:
        """
        One-off sync: ensure sprint, set default, verify, and create future sprints.

        Args:
            board (str): Agile board name.
            project (str): Project name.
            field (str): Sprint field name.
            week (str | None): Week in YYYY.WW format or None for current.
            forward (int): How many future sprints to create.
        """
        year, week_num, sprint_name, monday, friday, start_ms, finish_ms = DateUtils.process_week_parameter(week)

        logger.info("📅 Week: %s.%02d (%s - %s)", year, week_num, monday, friday)
        logger.info("🏃 Sprint: %s", sprint_name)

        self.ensure_sprint_on_board(board, sprint_name, start_ms, finish_ms)
        project_id, field_id = self.set_project_default_sprint(project, field, sprint_name)
        self.verify_project_default(project_id, field_id)
        self.ensure_future_sprints(board, year, week_num, max(0, int(forward)))

    def create_sprint_for_week(self, board_name: str, week_param: Optional[str]) -> None:
        """
        Create a sprint for a given ISO week (or current).

        If the sprint already exists, exits the process with code 0 (CLI semantics).

        Args:
            board_name (str): Agile board name.
            week_param (str | None): Week in YYYY.WW format or None for current.

        Raises:
            SystemExit: If board is not found, or to return 0 when sprint exists.
        """
        year, week, sprint_name, monday, friday, start_ms, finish_ms = DateUtils.process_week_parameter(week_param)
        logger.info("📅 Week: %s.%02d (%s - %s)", year, week, monday, friday)
        logger.info("🏃 Sprint: %s", sprint_name)

        board_id = self.yt.find_board_id(board_name)
        if not board_id:
            logger.error("❌ Board '%s' not found", board_name)
            raise SystemExit(1)
        logger.info("✅ BOARD_ID = %s", board_id)

        if self.yt.sprint_exists(board_id, sprint_name):
            logger.warning("⚠️ Sprint '%s' already exists", sprint_name)
            sys.exit(0)

        sprint_data = {"name": sprint_name, "start_ms": start_ms, "finish_ms": finish_ms}
        sprint = self.yt.create_sprint(board_id, sprint_data)
        logger.info("✅ Created sprint: %s (ID: %s)", sprint.get("name"), sprint.get("id"))
        logger.info("🎉 Done!")
