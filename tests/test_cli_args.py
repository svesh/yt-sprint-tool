#!/usr/bin/env python3
"""
Argument parsing tests for CLI modules.

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
import sys
from types import SimpleNamespace

from ytsprint.default_sprint import parse_args as ds_parse
from ytsprint.make_sprint import parse_args as ms_parse


def _with_argv(argv, func):  # type: ignore[no-untyped-def]
    """Helper to temporarily set sys.argv and call func()."""
    old = sys.argv[:]  # backup
    try:
        sys.argv = argv[:]  # replace
        return func()
    finally:
        sys.argv = old


def test_default_sprint_parse_args_basic() -> None:
    """Parse default-sprint minimal args and verify defaults."""
    argv = [
        "default-sprint",
        "Board",
        "Project",
    ]
    ns = _with_argv(argv, ds_parse)
    assert ns.board == "Board"
    assert ns.project == "Project"
    assert ns.field == "Sprints"
    assert ns.week is None
    assert ns.forward == 0
    assert ns.cron == "0 8 * * 1"


def test_default_sprint_parse_args_all_flags() -> None:
    """Parse default-sprint with all flags and verify values."""
    argv = [
        "default-sprint",
        "Board",
        "Project",
        "--field",
        "Custom",
        "--week",
        "2025.30",
        "--forward",
        "2",
        "--daemon",
        "--cron",
        "0 9 * * 2",
        "--metrics-addr",
        "127.0.0.1",
        "--metrics-port",
        "9999",
        "--url",
        "https://yt",
        "--token",
        "tok",
    ]
    ns = _with_argv(argv, ds_parse)
    assert ns.field == "Custom"
    assert ns.week == "2025.30"
    assert ns.forward == 2
    assert ns.daemon is True
    assert ns.cron == "0 9 * * 2"
    assert ns.metrics_addr == "127.0.0.1"
    assert ns.metrics_port == 9999
    assert ns.url == "https://yt"
    assert ns.token == "tok"


def test_make_sprint_parse_args_basic() -> None:
    """Parse make-sprint minimal args and verify defaults."""
    argv = [
        "make-sprint",
        "Board",
    ]
    ns = _with_argv(argv, ms_parse)
    assert ns.board == "Board"
    assert ns.week is None


def test_make_sprint_parse_args_with_week() -> None:
    """Parse make-sprint with week and auth flags."""
    argv = [
        "make-sprint",
        "Board",
        "2025.30",
        "--url",
        "https://yt",
        "--token",
        "t",
    ]
    ns: SimpleNamespace = _with_argv(argv, ms_parse)
    assert ns.board == "Board"
    assert ns.week == "2025.30"
    assert ns.url == "https://yt"
    assert ns.token == "t"
