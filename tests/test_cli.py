#!/usr/bin/env python3
"""Tests for unified ytsprint CLI."""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Any

import pytest

from ytsprint import cli

# pylint: disable=missing-function-docstring


class DummyService:
    """Test double for SprintService."""

    def __init__(self) -> None:
        self.sync_calls: list[tuple[str, str, str, str | None, int]] = []
        self.create_calls: list[tuple[str, str | None]] = []

    def run_sync_once(self, board: str, project: str, field: str, week: str | None, forward: int) -> None:
        self.sync_calls.append((board, project, field, week, forward))

    def create_sprint_for_week(self, board: str, week: str | None) -> None:
        self.create_calls.append((board, week))


def _with_argv(argv: list[str], func: Callable[[], Any]) -> Any:
    """Temporarily replace sys.argv for tests."""

    old = sys.argv[:]
    try:
        sys.argv = argv[:]
        return func()
    finally:
        sys.argv = old


def _service_factory(service: DummyService) -> Callable[[str, str], DummyService]:
    """Return typed factory that ignores credentials and yields the test service."""

    def _factory(url: str, token: str) -> DummyService:
        _ = url, token
        return service

    return _factory


def _noop_logging(_: str) -> None:
    """Typed stub for logging configuration hook."""


def test_parse_args_defaults_to_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    """By default CLI operates in sync mode."""

    monkeypatch.delenv("YTSPRINT_FORWARD", raising=False)
    monkeypatch.setattr(sys, "argv", ["ytsprint", "--board", "B", "--project", "P"])
    args = cli.parse_args()
    assert args.mode == "sync"


def test_main_create_executes_service(monkeypatch: pytest.MonkeyPatch) -> None:
    """--create mode calls SprintService.create_sprint_for_week."""

    service = DummyService()
    monkeypatch.setattr(cli, "_init_service", _service_factory(service))
    monkeypatch.setattr(cli, "_configure_logging", _noop_logging)

    argv = [
        "ytsprint",
        "--create",
        "--board",
        "Board",
        "--week",
        "2025.30",
        "--url",
        "https://yt",
        "--token",
        "tok",
    ]
    _with_argv(argv, cli.main)

    assert service.create_calls == [("Board", "2025.30")]
    assert not service.sync_calls


def test_main_sync_executes_run_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default sync mode triggers SprintService.run_sync_once once."""

    service = DummyService()
    monkeypatch.setattr(cli, "_init_service", _service_factory(service))
    monkeypatch.setattr(cli, "_configure_logging", _noop_logging)

    argv = [
        "ytsprint",
        "--board",
        "Board",
        "--project",
        "Project",
        "--field",
        "Custom",
        "--forward",
        "2",
        "--url",
        "https://yt",
        "--token",
        "tok",
    ]
    _with_argv(argv, cli.main)

    assert service.sync_calls == [("Board", "Project", "Custom", None, 2)]
    assert not service.create_calls


def test_main_daemon_uses_runner(monkeypatch: pytest.MonkeyPatch) -> None:
    """In daemon mode DaemonRunner.start receives the job closure."""

    service = DummyService()
    monkeypatch.setattr(cli, "_init_service", _service_factory(service))
    monkeypatch.setattr(cli, "_configure_logging", _noop_logging)

    captured_job: list[Callable[[], None]] = []

    class DummyRunner:
        """Test runner capturing scheduled job."""

        def __init__(self, cron: str, addr: str, port: int) -> None:
            assert cron == "* * * * *"
            assert addr == "127.0.0.1"
            assert port == 9999

        def start(self, job: Callable[[], None]) -> None:
            captured_job.append(job)

    monkeypatch.setattr(cli, "DaemonRunner", DummyRunner)

    argv = [
        "ytsprint",
        "--board",
        "Board",
        "--project",
        "Project",
        "--daemon",
        "--cron",
        "* * * * *",
        "--metrics-addr",
        "127.0.0.1",
        "--metrics-port",
        "9999",
        "--url",
        "https://yt",
        "--token",
        "tok",
    ]
    _with_argv(argv, cli.main)

    assert len(captured_job) == 1
    assert not service.sync_calls  # job is scheduled but not yet run


def test_main_create_with_daemon_is_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """--daemon is not allowed in create mode."""

    service = DummyService()
    monkeypatch.setattr(cli, "_init_service", _service_factory(service))
    monkeypatch.setattr(cli, "_configure_logging", _noop_logging)

    argv = [
        "ytsprint",
        "--create",
        "--daemon",
        "--board",
        "Board",
        "--url",
        "https://yt",
        "--token",
        "tok",
    ]

    with pytest.raises(SystemExit) as exc:
        _with_argv(argv, cli.main)

    assert exc.value.code == 1
    assert not service.create_calls


def test_main_missing_board_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    """Board is required regardless of mode."""

    monkeypatch.setattr(cli, "_configure_logging", _noop_logging)
    monkeypatch.setattr(cli, "_init_service", _service_factory(DummyService()))

    argv = ["ytsprint", "--project", "Project", "--url", "https://yt", "--token", "tok"]

    with pytest.raises(SystemExit) as exc:
        _with_argv(argv, cli.main)

    assert exc.value.code == 1
