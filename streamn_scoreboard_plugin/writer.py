"""Text file writer for OBS scoreboard output files."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from streamn_scoreboard_plugin.sport_mapping import get_game_init_values

log: logging.Logger = logging.getLogger(__name__)

_TIMESTAMP_RE: re.Pattern[str] = re.compile(r"^(\d+:\d{2}:\d{2})\s+(.+)$")


def parse_timestamps(content: str) -> list[dict[str, str]]:
    """Parse OBS scoreboard ``timestamps.txt`` into structured events.

    Each non-blank line is expected to match ``H:MM:SS Description``.
    Malformed lines are silently skipped.

    Returns a list of dicts with ``timestamp`` and ``description`` keys,
    matching the contract expected by the Google plugin.
    """
    events: list[dict[str, str]] = []
    for line in content.splitlines():
        match = _TIMESTAMP_RE.match(line.strip())
        if match:
            events.append({"timestamp": match.group(1), "description": match.group(2)})
    return events

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
    "default_penalty_duration": "default_penalty_duration.txt",
    "default_major_penalty_duration": "default_major_penalty_duration.txt",
    "home_faceoffs": "home_faceoffs.txt",
    "away_faceoffs": "away_faceoffs.txt",
    "period_labels": "period_labels.txt",
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

    def clear_timestamps(self) -> None:
        """Remove stale timestamps.txt from a previous game session."""
        timestamps_path = self._output_dir / "timestamps.txt"
        if timestamps_path.exists():
            timestamps_path.unlink()

    def write_game_finish(self, game_dir: Path) -> Path | None:
        """Copy timestamps from OBS output to the game directory as chapters.

        Reads ``timestamps.txt`` from the scoreboard output directory and
        writes it verbatim to ``chapters.txt`` in *game_dir*.

        Returns the path to the written file, or ``None`` if no timestamps
        were available.
        """
        timestamps_path = self._output_dir / "timestamps.txt"
        if not timestamps_path.exists():
            log.warning("Scoreboard plugin: timestamps.txt not found in %s", self._output_dir)
            return None

        content = timestamps_path.read_text(encoding="utf-8")
        if not content.strip():
            log.warning("Scoreboard plugin: timestamps.txt is empty")
            return None

        chapters_path = game_dir / "chapters.txt"
        chapters_path.write_text(content, encoding="utf-8")
        return chapters_path
