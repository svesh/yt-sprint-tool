#!/usr/bin/env python3
"""Tests for DaemonRunner helpers."""

# pylint: disable=missing-function-docstring,missing-class-docstring,protected-access,unused-argument,no-member

from __future__ import annotations

import math
from typing import Callable

import pytest

import ytsprint.lib_daemon as daemon
from ytsprint.lib_daemon import DaemonRunner


def _noop_http_server(**_: object) -> None:
    """No-op stub for start_http_server."""


def _raise_keyboard_interrupt(_: float) -> None:
    """time.sleep replacement raising KeyboardInterrupt immediately."""

    raise KeyboardInterrupt


class StubGauge:
    """Gauge replacement capturing set_function/set calls."""

    instances: list["StubGauge"] = []

    def __init__(self, name: str, doc: str) -> None:
        self.name = name
        self.doc = doc
        self.func: Callable[[], float] | None = None
        self.values: list[float] = []
        StubGauge.instances.append(self)

    def set_function(self, func: Callable[[], float]) -> None:
        self.func = func

    def set(self, value: float) -> None:
        self.values.append(value)


def test_init_metrics_installs_seconds_callback() -> None:
    """_init_metrics wires seconds gauge callback and returns status gauge/state."""

    StubGauge.instances.clear()
    status_gauge, state = DaemonRunner._init_metrics(StubGauge)  # type: ignore[arg-type]

    assert len(StubGauge.instances) == 2
    seconds_gauge = StubGauge.instances[0]
    returned_status = StubGauge.instances[1]
    assert returned_status is status_gauge
    assert seconds_gauge.func is not None
    assert math.isnan(seconds_gauge.func())  # type: ignore[operator]

    state["last_run_ts"] = 0.0
    assert seconds_gauge.func() >= 0.0  # type: ignore[operator]


def test_start_updates_metrics_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """start() runs job once, updates status gauge and shuts down scheduler."""

    StubGauge.instances.clear()
    monkeypatch.setattr(daemon, "Gauge", StubGauge)
    monkeypatch.setattr(daemon, "start_http_server", _noop_http_server)

    captured: list[str] = []

    class StubScheduler:
        """Scheduler stub invoking captured job immediately."""
        def __init__(self) -> None:
            self.job: Callable[[], None] | None = None
            self.shutdown_called = False

        def add_job(self, func: Callable[[], None], **_: object) -> None:
            self.job = func

        def start(self) -> None:
            if self.job:
                self.job()

        def shutdown(self, wait: bool = True) -> None:  # noqa: ARG002
            self.shutdown_called = True

    scheduler = StubScheduler()

    def fake_build(self: DaemonRunner, job: Callable[[], None]) -> StubScheduler:  # noqa: ARG001
        scheduler.add_job(job)
        scheduler.start()
        return scheduler

    monkeypatch.setattr(DaemonRunner, "_build_scheduler", fake_build, raising=False)
    monkeypatch.setattr(daemon.time, "sleep", _raise_keyboard_interrupt)

    runner = DaemonRunner("* * * * *", "127.0.0.1", 9000)
    runner.start(lambda: captured.append("ran"))

    assert captured == ["ran"]
    status_gauge = StubGauge.instances[1]
    assert status_gauge.values[-1] == 1.0
    assert scheduler.shutdown_called


def test_start_records_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """If job throws, status gauge records failure before shutdown."""

    StubGauge.instances.clear()
    monkeypatch.setattr(daemon, "Gauge", StubGauge)
    monkeypatch.setattr(daemon, "start_http_server", _noop_http_server)

    class StubScheduler:
        """Scheduler stub invoking captured job immediately."""
        def __init__(self) -> None:
            self.job: Callable[[], None] | None = None
            self.shutdown_called = False

        def add_job(self, func: Callable[[], None], **_: object) -> None:
            self.job = func

        def start(self) -> None:
            if self.job:
                self.job()

        def shutdown(self, wait: bool = True) -> None:  # noqa: ARG002
            self.shutdown_called = True

    scheduler = StubScheduler()

    def fake_build(self: DaemonRunner, job: Callable[[], None]) -> StubScheduler:  # noqa: ARG001
        scheduler.add_job(job)
        scheduler.start()
        return scheduler

    monkeypatch.setattr(DaemonRunner, "_build_scheduler", fake_build, raising=False)
    monkeypatch.setattr(daemon.time, "sleep", _raise_keyboard_interrupt)

    runner = DaemonRunner("* * * * *", "127.0.0.1", 9000)

    def failing_job() -> None:
        raise RuntimeError("boom")

    runner.start(failing_job)

    status_gauge = StubGauge.instances[1]
    assert status_gauge.values[-1] == 0.0
    assert scheduler.shutdown_called


def test_build_scheduler_uses_cron_trigger(monkeypatch: pytest.MonkeyPatch) -> None:
    """_build_scheduler wires cron trigger and starts scheduler."""

    captured_trigger: list[tuple[str, object]] = []

    class StubCronTrigger:
        @classmethod
        def from_crontab(cls, expr: str, timezone: object) -> str:
            captured_trigger.append((expr, timezone))
            return "trigger"

    class StubBackgroundScheduler:
        def __init__(self, **_: object) -> None:
            self.started = False
            self.jobs: list[tuple[Callable[[], None], object, object]] = []

        def add_job(self, func: Callable[[], None], *, trigger: object, next_run_time: object) -> None:
            self.jobs.append((func, trigger, next_run_time))

        def start(self) -> None:
            self.started = True

    monkeypatch.setattr(daemon, "BackgroundScheduler", StubBackgroundScheduler)
    monkeypatch.setattr(daemon, "CronTrigger", StubCronTrigger)

    runner = DaemonRunner("0 8 * * 1", "0.0.0.0", 9000)
    build_scheduler = getattr(runner, "_build_scheduler")
    scheduler = build_scheduler(lambda: None)

    assert captured_trigger[0][0] == "0 8 * * 1"
    assert isinstance(scheduler, StubBackgroundScheduler)
    stub_scheduler = scheduler
    assert stub_scheduler.started is True
    assert stub_scheduler.jobs
