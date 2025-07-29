#!/usr/bin/env python3
"""
Utilities for working with dates and weeks in YouTrack sprints.

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
"""

import argparse
import datetime as dt
from typing import Optional, Tuple

UTC = dt.timezone.utc


class DateUtils:
    """Class for working with dates and ISO weeks."""

    @staticmethod
    def iso_week_range_utc(year: int, week: int) -> Tuple[str, str, int, int]:
        """
        Returns ISO week date range (Monday-Friday) in UTC.

        Args:
            year (int): Year.
            week (int): ISO week number.

        Returns:
            tuple: (monday_iso, friday_iso, start_ms, finish_ms)
                - monday_iso (str): Monday date in ISO format.
                - friday_iso (str): Friday date in ISO format.
                - start_ms (int): Monday start in milliseconds UTC.
                - finish_ms (int): Friday end in milliseconds UTC.
        """
        monday = dt.date.fromisocalendar(year, week, 1)
        friday = dt.date.fromisocalendar(year, week, 5)

        start_utc = dt.datetime(monday.year, monday.month, monday.day, 0, 0, 0, tzinfo=UTC)
        finish_utc = dt.datetime(friday.year, friday.month, friday.day, 23, 59, 59, 999000, tzinfo=UTC)

        start_ms = int(start_utc.timestamp() * 1000)
        finish_ms = int(finish_utc.timestamp() * 1000)

        return monday.isoformat(), friday.isoformat(), start_ms, finish_ms

    @staticmethod
    def parse_year_week(spec: str) -> Tuple[int, int]:
        """
        Parses string in YYYY.WW format to year and week.

        Args:
            spec (str): String in YYYY.WW format (e.g., "2025.32").

        Returns:
            tuple: (year, week) - year and week number.

        Raises:
            argparse.ArgumentTypeError: For incorrect format.
        """
        try:
            year_str, week_str = spec.split(".")
            year = int(year_str)
            week = int(week_str)
            if not 1 <= week <= 53:
                raise ValueError("Week must be between 1 and 53")
            return year, week
        except Exception as exc:
            raise argparse.ArgumentTypeError("Expected format YYYY.WW, e.g. 2025.32") from exc

    @staticmethod
    def get_current_week() -> Tuple[int, int]:
        """
        Gets current ISO week.

        Returns:
            tuple: (year, week) - current year and week number.
        """
        today = dt.date.today()
        year, week, _ = today.isocalendar()
        return year, week

    @staticmethod
    def format_sprint_name(year: int, week: int) -> str:
        """
        Formats sprint name in standard format.

        Args:
            year (int): Year.
            week (int): Week number.

        Returns:
            str: Sprint name in "YYYY.WW Sprint" format.
        """
        return f"{year}.{week:02d} Sprint"

    @classmethod
    def process_week_parameter(cls, week_arg: Optional[str]) -> Tuple[int, int, str, str, str, int, int]:
        """
        Processes week parameter - either parses passed value or takes current.

        Args:
            week_arg (str or None): Week argument in YYYY.WW format or None.

        Returns:
            tuple: (year, week, sprint_name, monday, friday, start_ms, finish_ms)
        """
        if week_arg:
            year, week = cls.parse_year_week(week_arg)
        else:
            year, week = cls.get_current_week()

        sprint_name = cls.format_sprint_name(year, week)
        monday, friday, start_ms, finish_ms = cls.iso_week_range_utc(year, week)

        return year, week, sprint_name, monday, friday, start_ms, finish_ms
