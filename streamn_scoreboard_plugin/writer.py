"""Text file writer for OBS scoreboard output files."""

from __future__ import annotations

from pathlib import Path

from streamn_scoreboard_plugin.sport_mapping import get_game_init_values

# Filenames matching scoreboard-core.c write_all_files().
_FILENAMES: dict[str, str] = {
    "clock": "clock.txt",
    "period": "period.txt",
    "home_name": "home_name.txt",
    "away_name": "away_name.txt",
    "home_score": "home_score.txt",
    "away_score": "away_score.txt",
    "home_shots": "home_shots.txt",
    "away_shots": "away_shots.txt",
    "home_fouls": "home_fouls.txt",
    "away_fouls": "away_fouls.txt",
    "home_fouls2": "home_fouls2.txt",
    "away_fouls2": "away_fouls2.txt",
    "home_penalty_numbers": "home_penalty_numbers.txt",
    "home_penalty_times": "home_penalty_times.txt",
    "away_penalty_numbers": "away_penalty_numbers.txt",
    "away_penalty_times": "away_penalty_times.txt",
    "sport": "sport.txt",
}


class ScoreboardWriter:
    """Writes scoreboard state to text files in the output directory.

    Filenames are fixed to match the OBS scoreboard plugin's
    ``write_all_files()`` output format.
    """

    def __init__(self, output_directory: str | Path) -> None:
        self._output_dir = Path(output_directory)

    @property
    def output_directory(self) -> Path:
        """Return the configured output directory."""
        return self._output_dir

    def write_game_init(
        self,
        game_info: object,
        *,
        period_length: int | None = None,
    ) -> None:
        """Write initial game state to all scoreboard text files.

        Creates the output directory if it does not exist, then writes each
        scoreboard field to its text file.

        Parameters
        ----------
        game_info:
            Object with ``home_team``, ``away_team``, and ``sport`` attributes.
        period_length:
            When provided, overrides the sport-based clock duration.
        """
        self._output_dir.mkdir(parents=True, exist_ok=True)

        values = get_game_init_values(game_info, period_length=period_length)
        for key, content in values.items():
            filename = _FILENAMES[key]
            path = self._output_dir / filename
            path.write_text(content, encoding="utf-8")
