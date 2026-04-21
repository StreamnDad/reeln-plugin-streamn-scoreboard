"""Sport-to-scoreboard clock mapping."""

from __future__ import annotations

# Maps sport name to period duration in minutes (None = no clock / count up).
_SPORT_DURATION: dict[str, int | None] = {
    "hockey": 15,
    "basketball": 8,
    "soccer": 45,
    "football": 30,
    "lacrosse": 12,
    "rugby": 40,
    "baseball": None,
    "generic": None,
}

# Maps sport name to (minor_penalty_seconds, major_penalty_seconds).
# 0 means the sport has no penalty concept for that type.
_SPORT_PENALTY_DURATIONS: dict[str, tuple[int, int]] = {
    "hockey": (120, 300),
    "basketball": (0, 0),
    "soccer": (0, 0),
    "football": (0, 0),
    "lacrosse": (60, 180),
    "rugby": (120, 600),
    "generic": (120, 300),
}

# Maps sport name to (segment_count, ot_max).
# Used to generate default period labels.
_SPORT_PERIODS: dict[str, tuple[int, int]] = {
    "hockey": (3, 4),
    "basketball": (4, 1),
    "soccer": (2, 1),
    "football": (2, 1),
    "lacrosse": (4, 1),
    "rugby": (2, 1),
    "baseball": (9, 0),
    "generic": (1, 0),
}


def get_default_period_labels(sport: str) -> str:
    """Return newline-separated default period labels for *sport*."""
    segments, ot_max = _SPORT_PERIODS.get(sport, (1, 0))
    labels = [str(i + 1) for i in range(segments)]
    for i in range(ot_max):
        labels.append("OT" if i == 0 else f"OT{i + 1}")
    return "\n".join(labels) + "\n" if labels else "\n"


def format_clock(duration_minutes: int | None) -> str:
    """Format duration in minutes to scoreboard clock string.

    Matches ``scoreboard_clock_format()`` in scoreboard-core.c:
    ``%d:%02d`` — minutes unpadded, seconds zero-padded.
    """
    if duration_minutes is None:
        return "0:00"
    return f"{duration_minutes}:00"


def get_clock_for_sport(sport: str) -> str:
    """Return the formatted clock string for *sport*.

    Falls back to ``"0:00"`` for unknown sports.
    """
    duration = _SPORT_DURATION.get(sport)
    return format_clock(duration)


def get_game_init_values(
    game_info: object,
    *,
    period_length: int | None = None,
) -> dict[str, str]:
    """Build the full dict of scoreboard init values from a ``GameInfo`` instance.

    Parameters
    ----------
    game_info:
        Object with ``home_team``, ``away_team``, and ``sport`` attributes
        (``streamn.models.game.GameInfo``).
    period_length:
        When provided, overrides the sport-based clock with
        ``format_clock(period_length)``.

    Returns
    -------
    dict[str, str]
        Keys match ``ScoreboardWriter`` file keys; values are the initial text content.
    """
    sport: str = getattr(game_info, "sport", "generic")
    home_team: str = getattr(game_info, "home_team", "")
    away_team: str = getattr(game_info, "away_team", "")

    resolved_minutes: int = period_length if period_length is not None else (_SPORT_DURATION.get(sport) or 0)
    clock = format_clock(resolved_minutes if resolved_minutes else None)
    minor_secs, major_secs = _SPORT_PENALTY_DURATIONS.get(sport, (120, 300))
    period_labels: str = getattr(game_info, "period_labels", "") or get_default_period_labels(sport)

    return {
        "clock": clock,
        "period": "1",
        "home_name": home_team,
        "away_name": away_team,
        "home_score": "0",
        "away_score": "0",
        "home_shots": "0",
        "away_shots": "0",
        "home_fouls": "0",
        "away_fouls": "0",
        "home_fouls2": "0",
        "away_fouls2": "0",
        "home_faceoffs": "0",
        "away_faceoffs": "0",
        "home_penalty_numbers": "",
        "home_penalty_times": "",
        "away_penalty_numbers": "",
        "away_penalty_times": "",
        "sport": sport,
        "default_penalty_duration": str(minor_secs),
        "default_major_penalty_duration": str(major_secs),
        "period_labels": period_labels,
        "period_length": str(resolved_minutes * 60),
    }
