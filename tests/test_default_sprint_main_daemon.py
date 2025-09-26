#!/usr/bin/env python3
"""
Tests for default_sprint main and daemon runner paths.

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

import ytsprint.lib_daemon as daemon
from ytsprint import default_sprint as ds


def test_default_sprint_main_missing_auth(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """main should exit(1) when url/token are absent."""
    argv = ["default-sprint", "Board", "Project"]
    called = {"exit": None}

    def _fake_exit(code):  # type: ignore[no-untyped-def]
        called["exit"] = code
        raise SystemExit(code)

    monkeypatch.setattr("sys.argv", argv)
    monkeypatch.setattr("sys.exit", _fake_exit)

    try:
        ds.main()
    except SystemExit:  # expected
        pass

    assert called["exit"] == 1


def test_default_sprint_main_missing_board(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """main should exit(1) when board/project are absent and env unset."""
    argv = [
        "default-sprint",
        "--url",
        "https://yt",
        "--token",
        "tok",
    ]
    called = {"exit": None}

    def _fake_exit(code):  # type: ignore[no-untyped-def]
        called["exit"] = code
        raise SystemExit(code)

    monkeypatch.setattr("sys.argv", argv)
    monkeypatch.setattr("sys.exit", _fake_exit)

    try:
        ds.main()
    except SystemExit:  # expected
        pass

    assert called["exit"] == 1


def test_default_sprint_main_single_run(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """main should call run_once in non-daemon mode when auth present."""
    argv = [
        "default-sprint",
        "Board",
        "Project",
        "--url",
        "https://yt",
        "--token",
        "tok",
    ]
    called = {"count": 0}

    def _fake_run_once(self, board, project, field, week, forward):  # type: ignore[no-untyped-def]
        _ = self, board, project, field, week, forward
        called["count"] += 1

    # No-op YouTrackAPI
    class _Dummy:  # type: ignore[too-few-public-methods]
        def __init__(self, *_args, **_kwargs) -> None:  # noqa: D401
            """No-op client"""

    monkeypatch.setattr("sys.argv", argv)
    monkeypatch.setattr(ds.SprintService, "run_sync_once", _fake_run_once)
    monkeypatch.setattr(ds, "YouTrackAPI", _Dummy)

    ds.main()
    assert called["count"] == 1


class DummyScheduler:  # type: ignore[too-few-public-methods]
    """Minimal scheduler stub for daemon test."""

    def __init__(self, *_a, **_k):
        self.job = None

    def add_job(self, job_func, **_kwargs):
        """Register job and invoke immediately to simulate next_run_time=now."""
        self.job = job_func
        job_func()

    def start(self):
        """No-op."""

    def shutdown(self, wait=True):  # noqa: ARG002
        """No-op."""


class DummyCron:  # type: ignore[too-few-public-methods]
    """Minimal cron trigger stub."""

    @classmethod
    def from_crontab(cls, *_a, **_k):
        """Return a dummy trigger instance."""
        return cls()


class DummyGauge:  # type: ignore[too-few-public-methods]
    """Minimal Gauge stub with set and set_function."""

    def __init__(self, *_a, **_k):
        self.val = None
        self.fn = None

    def set_function(self, fn):  # type: ignore[no-untyped-def]
        """Register a function callback for gauge value."""
        self.fn = fn

    def set(self, x):  # type: ignore[no-untyped-def]
        """Set gauge value (stored for assertions)."""
        self.val = x


def test_start_daemon_success_then_interrupt(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """start_daemon should start, run one job, and stop on KeyboardInterrupt."""
    _ = MagicMock()  # no-op API placeholder
    args = {
        "board": "Board",
        "project": "Project",
        "field": "Sprints",
        "week": "2025.30",
        "forward": 0,
        "cron": "* * * * *",
        "metrics_addr": "127.0.0.1",
        "metrics_port": 9999,
    }

    called = {"count": 0}

    def _fake_run_once(*_a, **_k):  # type: ignore[no-untyped-def]
        called["count"] += 1

    monkeypatch.setattr(daemon, "BackgroundScheduler", DummyScheduler)
    monkeypatch.setattr(daemon, "CronTrigger", DummyCron)
    monkeypatch.setattr(daemon, "Gauge", DummyGauge)
    monkeypatch.setattr(daemon, "start_http_server", lambda **_k: None)
    with patch.object(daemon.time, "sleep", side_effect=KeyboardInterrupt):
        def _job():  # type: ignore[no-untyped-def]
            _fake_run_once(object(), args["board"], args["project"], args["field"], args["week"], args["forward"])

        runner = daemon.DaemonRunner(args["cron"], args["metrics_addr"], args["metrics_port"])
        runner.start(_job)

    assert called["count"] == 1
