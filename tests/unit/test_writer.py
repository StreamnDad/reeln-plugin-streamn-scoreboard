"""Tests for writer module."""

from __future__ import annotations

from pathlib import Path

from streamn_scoreboard_plugin.writer import ScoreboardWriter
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

    def test_writes_all_seventeen_files(self, output_dir: Path) -> None:
        writer = ScoreboardWriter(output_dir)
        writer.write_game_init(FakeGameInfo())

        files = list(output_dir.iterdir())
        assert len(files) == 17

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
