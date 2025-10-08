#!/usr/bin/env python3
"""
Tests for SprintService helpers (run_once and forward logic).

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

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import TypedDict, cast
from unittest.mock import MagicMock

import pytest

from ytsprint.lib_date_utils import DateUtils
from ytsprint.lib_sprint import SprintService
from ytsprint.lib_yt_api import YouTrackAPI


class BundleValue(TypedDict):
    """Bundle value entry with stable ID and name."""

    id: str
    name: str


class WeekInfo(TypedDict):
    """Expected ISO week metadata for future sprint validation."""

    year: int
    week: int
    name: str
    monday: str
    friday: str


class SprintPayload(TypedDict):
    """Payload structure used when creating sprints via the API mock."""

    name: str
    start_ms: int
    finish_ms: int


def _bundle_value_entry(name: str) -> BundleValue:
    """Return bundle value entry with deterministic ID for sprint name."""

    raw = name.replace(" Sprint", "")
    return {"id": f"val-{raw.replace('.', '-')}", "name": name}


def _mk_api_mock(existing_sprint_names: Sequence[str] | None = None) -> MagicMock:
    api = MagicMock()
    # Common lookups
    api.find_board_id.return_value = "board-1"
    api.find_project_id.return_value = "proj-1"

    # Bundle find by name should search inside provided values
    def _find_bundle_value_by_name(values: Iterable[BundleValue], name: str) -> str | None:
        for v in values:
            if v.get("name") == name:
                return v.get("id")
        return None

    api.find_bundle_value_by_name.side_effect = _find_bundle_value_by_name

    # Project fields include the Sprints field with a known value id for 2025.30
    sprint_names = list(existing_sprint_names) if existing_sprint_names else ["2025.30 Sprint", "2025.31 Sprint"]
    values: list[BundleValue] = [_bundle_value_entry(name) for name in sprint_names]
    api.get_project_fields.return_value = [
        {
            "id": "field-1",
            "field": {"name": "Sprints"},
            "bundle": {"values": values},
        }
    ]

    # Field defaults readback
    defaults: list[BundleValue] = [{"id": values[0]["id"], "name": values[0]["name"]}] if values else []
    api.get_field_defaults.return_value = {"field": {"name": "Sprints"}, "defaultValues": defaults}

    # Sprint creation returns a stub with ID so .get works as expected
    api.create_sprint.return_value = {"id": "new-sprint"}

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


def test_ensure_sprint_on_board_skips_existing() -> None:
    """ensure_sprint_on_board skips creation when sprint already present."""

    api = _mk_api_mock()
    api.find_sprint_id.return_value = "existing"

    SprintService(api).ensure_sprint_on_board("Board", "2025.30 Sprint", 1, 2)

    api.create_sprint.assert_not_called()


def test_set_project_default_sprint_success() -> None:
    """set_project_default_sprint updates project defaults when value exists."""

    api = _mk_api_mock()

    project_id, field_id = SprintService(api).set_project_default_sprint(
        "Project", "Sprints", "2025.30 Sprint"
    )

    assert project_id == "proj-1"
    assert field_id == "field-1"
    api.update_field_default_values.assert_called_once_with("proj-1", "field-1", ["val-2025-30"])


def test_ensure_future_sprints_creates_missing() -> None:
    """ensure_future_sprints skips existing sprints and creates missing ones."""

    api = _mk_api_mock()
    api.sprint_exists.side_effect = [True, False]

    SprintService(api).ensure_future_sprints("Board", 2025, 50, 2)

    assert api.create_sprint.call_count == 1
    created_payload = api.create_sprint.call_args[0][1]
    assert created_payload["name"] != ""
    assert created_payload["start_ms"] < created_payload["finish_ms"]


def test_create_sprint_for_week_skips_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    """create_sprint_for_week exits with code 0 when sprint already exists."""

    api = _mk_api_mock()
    api.sprint_exists.return_value = True

    def _week_param_stub(_cls: type[DateUtils], _week: str | None) -> tuple[int, int, str, str, str, int, int]:
        return 2025, 30, "2025.30 Sprint", "monday", "friday", 1, 2

    monkeypatch.setattr(DateUtils, "process_week_parameter", classmethod(_week_param_stub))

    service = SprintService(api)
    with pytest.raises(SystemExit) as exc:
        service.create_sprint_for_week("Board", None)
    assert exc.value.code == 0
    api.create_sprint.assert_not_called()


def test_create_sprint_for_week_creates_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """create_sprint_for_week creates sprint when absent."""

    api = _mk_api_mock()
    api.sprint_exists.return_value = False

    def _week_param_stub(_cls: type[DateUtils], _week: str | None) -> tuple[int, int, str, str, str, int, int]:
        return 2025, 31, "2025.31 Sprint", "monday", "friday", 10, 20

    monkeypatch.setattr(DateUtils, "process_week_parameter", classmethod(_week_param_stub))

    SprintService(api).create_sprint_for_week("Board", None)

    api.create_sprint.assert_called_once()


@pytest.mark.parametrize(
    ("week_spec", "expected_weeks"),
    [
        (
            "2023.51",
            [
                {"year": 2023, "week": 51, "name": "2023.51 Sprint", "monday": "2023-12-18", "friday": "2023-12-22"},
                {"year": 2023, "week": 52, "name": "2023.52 Sprint", "monday": "2023-12-25", "friday": "2023-12-29"},
                {"year": 2024, "week": 1, "name": "2024.01 Sprint", "monday": "2024-01-01", "friday": "2024-01-05"},
            ],
        ),
        (
            "2023.52",
            [
                {"year": 2023, "week": 52, "name": "2023.52 Sprint", "monday": "2023-12-25", "friday": "2023-12-29"},
                {"year": 2024, "week": 1, "name": "2024.01 Sprint", "monday": "2024-01-01", "friday": "2024-01-05"},
                {"year": 2024, "week": 2, "name": "2024.02 Sprint", "monday": "2024-01-08", "friday": "2024-01-12"},
            ],
        ),
        (
            "2025.51",
            [
                {"year": 2025, "week": 51, "name": "2025.51 Sprint", "monday": "2025-12-15", "friday": "2025-12-19"},
                {"year": 2025, "week": 52, "name": "2025.52 Sprint", "monday": "2025-12-22", "friday": "2025-12-26"},
                {"year": 2026, "week": 1, "name": "2026.01 Sprint", "monday": "2025-12-29", "friday": "2026-01-02"},
            ],
        ),
        (
            "2025.52",
            [
                {"year": 2025, "week": 52, "name": "2025.52 Sprint", "monday": "2025-12-22", "friday": "2025-12-26"},
                {"year": 2026, "week": 1, "name": "2026.01 Sprint", "monday": "2025-12-29", "friday": "2026-01-02"},
                {"year": 2026, "week": 2, "name": "2026.02 Sprint", "monday": "2026-01-05", "friday": "2026-01-09"},
            ],
        ),
        (
            "2026.52",
            [
                {"year": 2026, "week": 52, "name": "2026.52 Sprint", "monday": "2026-12-21", "friday": "2026-12-25"},
                {"year": 2026, "week": 53, "name": "2026.53 Sprint", "monday": "2026-12-28", "friday": "2027-01-01"},
                {"year": 2027, "week": 1, "name": "2027.01 Sprint", "monday": "2027-01-04", "friday": "2027-01-08"},
            ],
        ),
        (
            "2026.53",
            [
                {"year": 2026, "week": 53, "name": "2026.53 Sprint", "monday": "2026-12-28", "friday": "2027-01-01"},
                {"year": 2027, "week": 1, "name": "2027.01 Sprint", "monday": "2027-01-04", "friday": "2027-01-08"},
                {"year": 2027, "week": 2, "name": "2027.02 Sprint", "monday": "2027-01-11", "friday": "2027-01-15"},
            ],
        ),
    ],
)
def test_run_once_forward_year_boundaries(week_spec: str, expected_weeks: Sequence[WeekInfo]) -> None:
    """Forward creation handles ISO week transitions across year boundaries."""

    current_name = expected_weeks[0]["name"]

    api = _mk_api_mock([current_name])
    api.find_sprint_id.return_value = None
    api.sprint_exists.return_value = False

    SprintService(api).run_sync_once(
        board="Board", project="Project", field="Sprints", week=week_spec, forward=2
    )

    assert api.create_sprint.call_count == len(expected_weeks)
    for call_obj, expected in zip(api.create_sprint.call_args_list, expected_weeks):
        board_id, payload = cast(tuple[str, SprintPayload], call_obj.args)
        assert board_id == "board-1"
        assert payload["name"] == expected["name"]

        monday, friday, start_ms, finish_ms = DateUtils.iso_week_range_utc(expected["year"], expected["week"])
        assert monday == expected["monday"]
        assert friday == expected["friday"]
        assert payload["start_ms"] == start_ms
        assert payload["finish_ms"] == finish_ms

    expected_default_id = f"val-{expected_weeks[0]['year']}-{expected_weeks[0]['week']:02d}"
    api.update_field_default_values.assert_called_once_with("proj-1", "field-1", [expected_default_id])


def test_update_field_default_values_idempotent_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    """When current defaults equal desired, API performs no changes."""

    api = YouTrackAPI(base_url="https://example", token="t")

    # Mock underlying HTTP calls
    get_mock = MagicMock(return_value=[{"id": "val-2025-30"}])
    delete_mock = MagicMock()
    post_mock = MagicMock()

    monkeypatch.setattr(api, "get", get_mock)
    monkeypatch.setattr(api, "delete", delete_mock)
    monkeypatch.setattr(api, "post", post_mock)

    api.update_field_default_values("proj", "field", ["val-2025-30"])

    delete_mock.assert_not_called()
    post_mock.assert_not_called()


def test_update_field_default_values_remove_only_incorrect(monkeypatch: pytest.MonkeyPatch) -> None:
    """Removes only values not in desired set and keeps the correct one."""

    api = YouTrackAPI(base_url="https://example", token="t")

    # Current defaults contain both correct and incorrect
    get_mock = MagicMock(return_value=[{"id": "val-2025-30"}, {"id": "val-OLD"}])
    delete_mock = MagicMock(return_value=204)
    post_mock = MagicMock()

    monkeypatch.setattr(api, "get", get_mock)
    monkeypatch.setattr(api, "delete", delete_mock)
    monkeypatch.setattr(api, "post", post_mock)

    api.update_field_default_values("proj", "field", ["val-2025-30"])

    # Only the incorrect one removed; nothing added
    delete_calls = [call.args[0] for call in delete_mock.call_args_list]
    assert any("val-OLD" in url for url in delete_calls)
    assert not any("val-2025-30" in url for url in delete_calls)
    post_mock.assert_not_called()


def test_update_field_default_values_add_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Adds missing desired default when none are set currently."""

    api = YouTrackAPI(base_url="https://example", token="t")

    get_mock = MagicMock(return_value=[])
    delete_mock = MagicMock()
    post_mock = MagicMock()

    monkeypatch.setattr(api, "get", get_mock)
    monkeypatch.setattr(api, "delete", delete_mock)
    monkeypatch.setattr(api, "post", post_mock)

    api.update_field_default_values("proj", "field", ["val-2025-30"])

    delete_mock.assert_not_called()
    post_mock.assert_called_once()
