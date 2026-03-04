"""Sport-to-scoreboard clock mapping."""

from __future__ import annotations

# Maps sport name to period duration in minutes (None = no clock / count up).
_SPORT_DURATION: dict[str, int | None] = {
    "hockey": 20,
    "basketball": 12,
    "soccer": 45,
    "football": 30,
    "lacrosse": 12,
    "rugby": 40,
    "baseball": None,
    "generic": None,
}


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

    clock = format_clock(period_length) if period_length is not None else get_clock_for_sport(sport)

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
        "home_penalty_numbers": "",
        "home_penalty_times": "",
        "away_penalty_numbers": "",
        "away_penalty_times": "",
        "sport": sport,
    }
