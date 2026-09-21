"""Smoke test that records which interpreter and environment ran it."""

import os
import sys


def test_reports_environment() -> None:
    """Assert Python is in the supported range and surface the environment name."""
    env = os.environ.get("PIXI_ENVIRONMENT_NAME", "?")
    version = ".".join(str(part) for part in sys.version_info[:3])
    assert sys.version_info >= (3, 12), f"env={env} python={version}"
