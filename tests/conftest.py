#!/usr/bin/env python3
"""Common pytest fixtures and test configuration."""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture(autouse=True)
def clear_youtrack_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove YouTrack credentials from the environment for every test."""

    for key in (
        "YOUTRACK_URL",
        "YOUTRACK_TOKEN",
        "YOUTRACK_BOARD",
        "YOUTRACK_PROJECT",
        "YTSPRINT_CRON",
        "YTSPRINT_FORWARD",
        "YTSPRINT_LOG_LEVEL",
    ):
        monkeypatch.delenv(key, raising=False)
