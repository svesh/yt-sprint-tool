#!/usr/bin/env python3
"""
Tests for default_sprint CLI helpers (run_once and forward logic).

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

from unittest.mock import MagicMock

from ytsprint.lib_date_utils import DateUtils
from ytsprint.lib_sprint import SprintService


def _mk_api_mock() -> MagicMock:
    api = MagicMock()
    # Common lookups
    api.find_board_id.return_value = "board-1"
    api.find_project_id.return_value = "proj-1"

    # Bundle find by name should search inside provided values
    def _find_bundle_value_by_name(values, name):
        for v in values:
            if v.get("name") == name:
                return v.get("id")
        return None

    api.find_bundle_value_by_name.side_effect = _find_bundle_value_by_name

    # Project fields include the Sprints field with a known value id for 2025.30
    api.get_project_fields.return_value = [
        {
            "id": "field-1",
            "field": {"name": "Sprints"},
            "bundle": {
                "values": [
                    {"id": "val-2025-30", "name": "2025.30 Sprint"},
                    {"id": "val-2025-31", "name": "2025.31 Sprint"},
                ]
            },
        }
    ]

    # Field defaults readback
    api.get_field_defaults.return_value = {
        "field": {"name": "Sprints"},
        "defaultValues": [{"id": "val-2025-30", "name": "2025.30 Sprint"}],
    }

    return api


def test_run_once_creates_current_and_sets_default() -> None:
    """run_once creates current sprint and switches default value."""
    api = _mk_api_mock()

    # Force sprint not found to trigger creation
    api.find_sprint_id.return_value = None

    SprintService(api).run_sync_once(board="Board", project="Project", field="Sprints", week="2025.30", forward=0)

    # Created exactly one sprint for 2025.30
    year, week = 2025, 30
    _, _, start_ms, finish_ms = DateUtils.iso_week_range_utc(year, week)
    api.create_sprint.assert_called_once_with(
        "board-1", {"name": "2025.30 Sprint", "start_ms": start_ms, "finish_ms": finish_ms}
    )

    # Default switched to that sprint
    api.update_field_default_values.assert_called_once_with("proj-1", "field-1", ["val-2025-30"])


def test_run_once_creates_forward_sprints() -> None:
    """run_once creates forward sprints when --forward > 0."""
    api = _mk_api_mock()
    # Current sprint creation
    api.find_sprint_id.return_value = None

    # For forward sprint existence check: ensure doesn't exist
    api.sprint_exists.return_value = False

    SprintService(api).run_sync_once(board="Board", project="Project", field="Sprints", week="2025.30", forward=1)

    # Current + one future should be created
    assert api.create_sprint.call_count == 2
