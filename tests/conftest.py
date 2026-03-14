"""Shared test fixtures."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
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


@dataclass
class FakeGameState:
    """Minimal stand-in for ``reeln.models.game.GameState``."""

    game_info: FakeGameInfo = field(default_factory=FakeGameInfo)
    finished: bool = True
    finished_at: str = "2026-03-13T18:00:00Z"


@pytest.fixture()
def game_info() -> FakeGameInfo:
    return FakeGameInfo()


@pytest.fixture()
def game_dir(tmp_path: Any) -> Path:
    """Return a temporary game directory path (simulates reeln game dir)."""
    d = tmp_path / "game_dir"
    d.mkdir()
    return d


@pytest.fixture()
def output_dir(tmp_path: Any) -> Any:
    """Return a temporary output directory path."""
    return tmp_path / "scoreboard_output"


@pytest.fixture()
def plugin_config(output_dir: Any) -> dict[str, Any]:
    """Return a minimal valid plugin config."""
    return {"output_directory": str(output_dir)}
