#!/usr/bin/env python3
"""
Daemon and Prometheus monitoring utilities for YT Sprint Tool.

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

Class-based API: DaemonRunner(cron, metrics_addr, metrics_port).start(job_func)

This module now imports APScheduler and prometheus_client at module load time,
making daemon dependencies mandatory for the runtime build.
"""

from __future__ import annotations

import datetime as dt
import logging
import time
from typing import Any, Callable, Dict, Optional, Tuple

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from prometheus_client import Gauge, start_http_server

logger = logging.getLogger(__name__)


class DaemonRunner:
    """
    Runs a background cron job with Prometheus metrics exporter.

    Args:
        cron (str): Crontab string in APScheduler/cron format (UTC).
        metrics_addr (str): Address to bind Prometheus exporter to. Defaults to "0.0.0.0".
        metrics_port (int): Port for Prometheus exporter. Defaults to 9108.
    """

    def __init__(self, cron: str, metrics_addr: str = "0.0.0.0", metrics_port: int = 9108) -> None:
        """Store configuration for the runner."""
        self.cron = cron
        self.metrics_addr = metrics_addr
        self.metrics_port = int(metrics_port)

    @staticmethod
    def _init_metrics(gauge_cls: Any) -> Tuple[Any, Dict[str, Optional[float]]]:
        """
        Initialize Prometheus gauges and shared state.

        Args:
            gauge_cls (type): prometheus_client.Gauge class.

        Returns:
            tuple: (status_gauge, state_dict)
        """
        state: Dict[str, Optional[float]] = {"last_run_ts": None, "last_status": 0.0}

        seconds_gauge = gauge_cls("ytsprint_cron_seconds", "Seconds since last cron run")
        status_gauge = gauge_cls("ytsprint_cron_status", "Last cron run status: 1=success, 0=failure")

        def _seconds() -> float:
            if state["last_run_ts"] is None:
                return float("nan")
            return max(0.0, time.time() - float(state["last_run_ts"]))

        seconds_gauge.set_function(_seconds)
        return status_gauge, state

    def _build_scheduler(self, job_func: Callable[[], None]) -> BackgroundScheduler:
        """Build and start APScheduler with cron trigger (UTC)."""

        scheduler = BackgroundScheduler(
            timezone=dt.timezone.utc,
            job_defaults={"coalesce": False, "misfire_grace_time": 30},
        )
        trigger = CronTrigger.from_crontab(self.cron, timezone=dt.timezone.utc)
        scheduler.add_job(job_func, trigger=trigger, next_run_time=dt.datetime.now(dt.timezone.utc))
        scheduler.start()
        return scheduler

    def start(self, job_func: Callable[[], None]) -> None:
        """
        Start the daemon: schedule job and expose Prometheus metrics.

        Args:
            job_func (Callable): Function to execute on each scheduled tick.

        Raises:
            SystemExit: If required dependencies cannot be imported.
        """
        logger.info("Starting daemon mode (UTC)...")
        status_gauge, state = self._init_metrics(Gauge)
        start_http_server(addr=self.metrics_addr, port=self.metrics_port)
        logger.info("Prometheus exporter: http://%s:%s/metrics", self.metrics_addr, self.metrics_port)

        def _job_wrapper() -> None:
            state["last_run_ts"] = time.time()
            try:
                job_func()
                state["last_status"] = 1.0
            except Exception as job_exc:  # pylint: disable=broad-exception-caught
                state["last_status"] = 0.0
                logger.exception("Cron job failed: %s", job_exc)
            finally:
                val = 0.0 if state["last_status"] is None else float(state["last_status"])  # type: ignore[arg-type]
                status_gauge.set(val)

        scheduler = self._build_scheduler(_job_wrapper)
        logger.info("Cron schedule (UTC): %s", self.cron)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping daemon...")
            scheduler.shutdown(wait=True)  # type: ignore[attr-defined]
