#!/usr/bin/env python3
"""
Tests for make_sprint CLI helper.

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

from ytsprint import make_sprint as make_cli
from ytsprint.make_sprint import create_sprint


def test_create_sprint_creates_when_missing() -> None:  # type: ignore[no-untyped-def]
    """create_sprint creates a new sprint when it doesn't exist."""
    api = MagicMock()
    api.find_board_id.return_value = "board-1"
    api.sprint_exists.return_value = False
    api.create_sprint.return_value = {"id": "sprint-id", "name": "2025.30 Sprint"}

    create_sprint(api, "Board", "2025.30")

    assert api.create_sprint.called


def test_create_sprint_exits_when_exists(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """create_sprint exits(0) when the sprint already exists."""
    api = MagicMock()
    api.find_board_id.return_value = "board-1"
    api.sprint_exists.return_value = True
    # Prevent sys.exit from aborting test
    called = {"exit": None}

    def _fake_exit(code):  # type: ignore[no-untyped-def]
        called["exit"] = code
        raise SystemExit(code)

    monkeypatch.setattr("sys.exit", _fake_exit)

    try:
        create_sprint(api, "Board", "2025.30")
    except SystemExit:  # expected
        pass

    assert called["exit"] == 0


def test_make_sprint_main_missing_auth(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """main should exit(1) when url/token are absent."""
    argv = ["make-sprint", "Board"]

    called = {"exit": None}

    def _fake_exit(code):  # type: ignore[no-untyped-def]
        called["exit"] = code
        raise SystemExit(code)

    monkeypatch.setattr("sys.argv", argv)
    monkeypatch.setattr("sys.exit", _fake_exit)

    try:
        make_cli.main()
    except SystemExit:  # expected
        pass

    assert called["exit"] == 1


def test_make_sprint_main_happy_path(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """main should call create_sprint when auth present."""
    argv = ["make-sprint", "Board", "2025.30", "--url", "https://yt", "--token", "tok"]
    called = {"count": 0}

    def _fake_create(yt, board, week):  # type: ignore[no-untyped-def]
        _ = yt, board, week
        called["count"] += 1

    monkeypatch.setattr("sys.argv", argv)
    monkeypatch.setattr(make_cli, "create_sprint", _fake_create)

    # Patch YouTrackAPI to a no-op class
    class _Dummy:  # type: ignore[too-few-public-methods]
        def __init__(self, *_args, **_kwargs) -> None:  # noqa: D401
            """No-op client"""

    monkeypatch.setattr(make_cli, "YouTrackAPI", _Dummy)

    make_cli.main()
    assert called["count"] == 1
