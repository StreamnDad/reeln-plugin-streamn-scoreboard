"""Shared test fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest


@dataclass
class FakeGameInfo:
    """Minimal stand-in for ``streamn.models.game.GameInfo``."""

    date: str = "2026-01-15"
    home_team: str = "Eagles"
    away_team: str = "Hawks"
    sport: str = "hockey"
    game_number: int = 1
    venue: str = ""
    period_length: int = 0


@dataclass
class FakeTeamProfile:
    """Minimal stand-in for ``reeln.models.team.TeamProfile``."""

    team_name: str = "Eagles"
    short_name: str = "EGL"
    level: str = "varsity"
    period_length: int = 15


@pytest.fixture()
def game_info() -> FakeGameInfo:
    return FakeGameInfo()


@pytest.fixture()
def output_dir(tmp_path: Any) -> Any:
    """Return a temporary output directory path."""
    return tmp_path / "scoreboard_output"


@pytest.fixture()
def plugin_config(output_dir: Any) -> dict[str, Any]:
    """Return a minimal valid plugin config."""
    return {"output_directory": str(output_dir)}
