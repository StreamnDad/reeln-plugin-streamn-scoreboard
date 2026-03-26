"""Tests for writer module."""

from __future__ import annotations

import logging
from pathlib import Path

from streamn_scoreboard_plugin.writer import ScoreboardWriter, parse_timestamps
from tests.conftest import FakeGameInfo


class TestScoreboardWriterInit:
    def test_uses_output_directory(self, output_dir: Path) -> None:
        writer = ScoreboardWriter(output_dir)
        assert writer.output_directory == output_dir

    def test_accepts_string_path(self, output_dir: Path) -> None:
        writer = ScoreboardWriter(str(output_dir))
        assert writer.output_directory == output_dir


class TestWriteGameInit:
    def test_creates_output_directory(self, output_dir: Path) -> None:
        writer = ScoreboardWriter(output_dir)
        writer.write_game_init(FakeGameInfo())
        assert output_dir.is_dir()

    def test_writes_all_twenty_files(self, output_dir: Path) -> None:
        writer = ScoreboardWriter(output_dir)
        writer.write_game_init(FakeGameInfo())

        files = list(output_dir.iterdir())
        assert len(files) == 22

    def test_hockey_file_contents(self, output_dir: Path) -> None:
        game_info = FakeGameInfo(home_team="Eagles", away_team="Hawks", sport="hockey")
        writer = ScoreboardWriter(output_dir)
        writer.write_game_init(game_info)

        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "20:00"
        assert (output_dir / "period.txt").read_text(encoding="utf-8") == "1"
        assert (output_dir / "home_name.txt").read_text(encoding="utf-8") == "Eagles"
        assert (output_dir / "away_name.txt").read_text(encoding="utf-8") == "Hawks"
        assert (output_dir / "home_score.txt").read_text(encoding="utf-8") == "0"
        assert (output_dir / "away_score.txt").read_text(encoding="utf-8") == "0"
        assert (output_dir / "home_shots.txt").read_text(encoding="utf-8") == "0"
        assert (output_dir / "away_shots.txt").read_text(encoding="utf-8") == "0"
        assert (output_dir / "home_fouls.txt").read_text(encoding="utf-8") == "0"
        assert (output_dir / "away_fouls.txt").read_text(encoding="utf-8") == "0"
        assert (output_dir / "home_fouls2.txt").read_text(encoding="utf-8") == "0"
        assert (output_dir / "away_fouls2.txt").read_text(encoding="utf-8") == "0"
        assert (output_dir / "home_penalty_numbers.txt").read_text(encoding="utf-8") == ""
        assert (output_dir / "home_penalty_times.txt").read_text(encoding="utf-8") == ""
        assert (output_dir / "away_penalty_numbers.txt").read_text(encoding="utf-8") == ""
        assert (output_dir / "away_penalty_times.txt").read_text(encoding="utf-8") == ""
        assert (output_dir / "sport.txt").read_text(encoding="utf-8") == "hockey"

    def test_existing_directory_no_error(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True)
        writer = ScoreboardWriter(output_dir)
        writer.write_game_init(FakeGameInfo())
        assert (output_dir / "clock.txt").exists()

    def test_overwrites_existing_files(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True)
        (output_dir / "home_score.txt").write_text("5", encoding="utf-8")

        writer = ScoreboardWriter(output_dir)
        writer.write_game_init(FakeGameInfo())
        assert (output_dir / "home_score.txt").read_text(encoding="utf-8") == "0"

    def test_period_length_overrides_clock(self, output_dir: Path) -> None:
        game_info = FakeGameInfo(sport="hockey")
        writer = ScoreboardWriter(output_dir)
        writer.write_game_init(game_info, period_length=17)
        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "17:00"

    def test_no_period_length_uses_sport(self, output_dir: Path) -> None:
        game_info = FakeGameInfo(sport="hockey")
        writer = ScoreboardWriter(output_dir)
        writer.write_game_init(game_info)
        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "20:00"


class TestWriteGameFinish:
    def test_copies_timestamps_to_game_dir(self, output_dir: Path, game_dir: Path) -> None:
        output_dir.mkdir(parents=True)
        timestamps = "0:00:00 Game Start\n0:12:34 Goal: Eagles (1-0)\n"
        (output_dir / "timestamps.txt").write_text(timestamps, encoding="utf-8")

        writer = ScoreboardWriter(output_dir)
        result = writer.write_game_finish(game_dir)

        assert result == game_dir / "chapters.txt"
        assert (game_dir / "chapters.txt").read_text(encoding="utf-8") == timestamps

    def test_no_timestamps_file_returns_none(
        self, output_dir: Path, game_dir: Path, caplog: logging.LogRecord
    ) -> None:
        output_dir.mkdir(parents=True)
        writer = ScoreboardWriter(output_dir)

        with caplog.at_level(logging.WARNING):
            result = writer.write_game_finish(game_dir)

        assert result is None
        assert "timestamps.txt not found" in caplog.text

    def test_empty_timestamps_returns_none(
        self, output_dir: Path, game_dir: Path, caplog: logging.LogRecord
    ) -> None:
        output_dir.mkdir(parents=True)
        (output_dir / "timestamps.txt").write_text("", encoding="utf-8")

        writer = ScoreboardWriter(output_dir)

        with caplog.at_level(logging.WARNING):
            result = writer.write_game_finish(game_dir)

        assert result is None
        assert "empty" in caplog.text

    def test_whitespace_only_timestamps_returns_none(
        self, output_dir: Path, game_dir: Path, caplog: logging.LogRecord
    ) -> None:
        output_dir.mkdir(parents=True)
        (output_dir / "timestamps.txt").write_text("  \n\n  ", encoding="utf-8")

        writer = ScoreboardWriter(output_dir)

        with caplog.at_level(logging.WARNING):
            result = writer.write_game_finish(game_dir)

        assert result is None
        assert "empty" in caplog.text

    def test_preserves_content_verbatim(self, output_dir: Path, game_dir: Path) -> None:
        output_dir.mkdir(parents=True)
        timestamps = "0:00:00 Game Start\n0:05:30 Goal: Eagles (1-0)\n0:47:00 End of Period 1\n"
        (output_dir / "timestamps.txt").write_text(timestamps, encoding="utf-8")

        writer = ScoreboardWriter(output_dir)
        writer.write_game_finish(game_dir)

        assert (game_dir / "chapters.txt").read_text(encoding="utf-8") == timestamps


class TestClearTimestamps:
    def test_removes_existing_timestamps_file(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True)
        timestamps_path = output_dir / "timestamps.txt"
        timestamps_path.write_text("0:00:00 Game Start\n", encoding="utf-8")

        writer = ScoreboardWriter(output_dir)
        writer.clear_timestamps()

        assert not timestamps_path.exists()

    def test_no_file_no_error(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True)
        writer = ScoreboardWriter(output_dir)
        writer.clear_timestamps()  # should not raise

    def test_does_not_affect_other_files(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True)
        (output_dir / "timestamps.txt").write_text("stale data", encoding="utf-8")
        (output_dir / "clock.txt").write_text("20:00", encoding="utf-8")

        writer = ScoreboardWriter(output_dir)
        writer.clear_timestamps()

        assert not (output_dir / "timestamps.txt").exists()
        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "20:00"


class TestParseTimestamps:
    def test_parses_standard_lines(self) -> None:
        content = "0:00:00 Game Start\n0:12:34 Goal: Eagles (1-0)\n"
        result = parse_timestamps(content)
        assert result == [
            {"timestamp": "0:00:00", "description": "Game Start"},
            {"timestamp": "0:12:34", "description": "Goal: Eagles (1-0)"},
        ]

    def test_multiple_events(self) -> None:
        content = (
            "0:00:00 Game Start\n"
            "0:05:30 Goal: Eagles (1-0)\n"
            "0:25:01 Penalty: Hawks #12\n"
            "0:40:15 End of Period 1\n"
        )
        result = parse_timestamps(content)
        assert len(result) == 4
        assert result[2] == {"timestamp": "0:25:01", "description": "Penalty: Hawks #12"}

    def test_empty_string_returns_empty_list(self) -> None:
        assert parse_timestamps("") == []

    def test_whitespace_only_returns_empty_list(self) -> None:
        assert parse_timestamps("  \n\n  ") == []

    def test_skips_blank_lines(self) -> None:
        content = "0:00:00 Game Start\n\n0:12:34 Goal: Eagles (1-0)\n"
        result = parse_timestamps(content)
        assert len(result) == 2

    def test_multi_digit_hours(self) -> None:
        content = "12:34:56 Overtime Goal\n"
        result = parse_timestamps(content)
        assert result == [{"timestamp": "12:34:56", "description": "Overtime Goal"}]

    def test_malformed_line_skipped(self) -> None:
        content = "0:00:00 Game Start\nno timestamp here\n0:12:34 Goal\n"
        result = parse_timestamps(content)
        assert len(result) == 2
        assert result[0]["description"] == "Game Start"
        assert result[1]["description"] == "Goal"
