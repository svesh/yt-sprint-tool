#!/usr/bin/env python3
"""
Error path tests for default_sprint helpers.

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
from unittest.mock import MagicMock, patch

import pytest

from ytsprint.lib_daemon import DaemonRunner
from ytsprint.lib_sprint import SprintService


def test_setup_sprint_board_not_found() -> None:  # type: ignore[no-untyped-def]
    """setup_sprint should exit(1) when board is not found."""
    api = MagicMock()
    api.find_board_id.return_value = None

    with pytest.raises(SystemExit) as exc:
        SprintService(api).ensure_sprint_on_board("Board", "2025.30 Sprint", 0, 1)
    assert exc.value.code == 1


def test_setup_project_field_missing_field() -> None:  # type: ignore[no-untyped-def]
    """setup_project_field should exit(1) when field is absent."""
    api = MagicMock()
    api.find_project_id.return_value = "proj"
    api.get_project_fields.return_value = [
        {"id": "f", "field": {"name": "Other"}, "bundle": {"values": []}}
    ]

    with pytest.raises(SystemExit) as exc:
        SprintService(api).set_project_default_sprint("Project", "Sprints", "2025.30 Sprint")
    assert exc.value.code == 1


def test_setup_project_field_value_not_found() -> None:  # type: ignore[no-untyped-def]
    """setup_project_field should exit(1) when bundle value missing."""
    api = MagicMock()
    api.find_project_id.return_value = "proj"
    api.get_project_fields.return_value = [
        {
            "id": "field-1",
            "field": {"name": "Sprints"},
            "bundle": {"values": [{"id": "x", "name": "2024.10 Sprint"}]},
        }
    ]
    api.find_bundle_value_by_name.return_value = None

    with pytest.raises(SystemExit) as exc:
        SprintService(api).set_project_default_sprint("Project", "Sprints", "2025.30 Sprint")
    assert exc.value.code == 1


def test_start_daemon_missing_deps() -> None:  # type: ignore[no-untyped-def]
    """DaemonRunner.start should exit(1) when deps cannot be imported."""
    # Force import failure
    with patch("importlib.import_module", side_effect=ImportError("no module")):
        with pytest.raises(SystemExit) as exc:
            DaemonRunner("* * * * *", metrics_addr="127.0.0.1", metrics_port=9999).start(lambda: None)
        assert exc.value.code == 1
