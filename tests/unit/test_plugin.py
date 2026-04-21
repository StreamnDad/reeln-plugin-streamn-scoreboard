"""Tests for plugin module."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pytest
from reeln.plugins.hooks import Hook, HookContext
from reeln.plugins.registry import HookRegistry

from streamn_scoreboard_plugin.plugin import ScoreboardPlugin
from tests.conftest import FakeGameInfo, FakeGameState, FakeTeamProfile


class TestScoreboardPluginAttributes:
    def test_name(self) -> None:
        plugin = ScoreboardPlugin()
        assert plugin.name == "streamn-scoreboard"

    def test_version(self) -> None:
        plugin = ScoreboardPlugin()
        assert plugin.version == "0.6.0"

    def test_api_version(self) -> None:
        plugin = ScoreboardPlugin()
        assert plugin.api_version == 1


class TestScoreboardPluginInit:
    def test_no_config(self) -> None:
        plugin = ScoreboardPlugin()
        assert plugin._writer is None

    def test_empty_config(self) -> None:
        plugin = ScoreboardPlugin({})
        assert plugin._writer is None

    def test_with_output_directory(self, plugin_config: dict[str, Any]) -> None:
        plugin = ScoreboardPlugin(plugin_config)
        assert plugin._writer is not None


class TestScoreboardPluginRegister:
    def test_registers_on_game_init(self) -> None:
        plugin = ScoreboardPlugin()
        registry = HookRegistry()
        plugin.register(registry)
        assert registry.has_handlers(Hook.ON_GAME_INIT)

    def test_registers_on_game_finish(self) -> None:
        plugin = ScoreboardPlugin()
        registry = HookRegistry()
        plugin.register(registry)
        assert registry.has_handlers(Hook.ON_GAME_FINISH)


class TestOnGameInit:
    def test_writes_files_on_hook(self, output_dir: Path, plugin_config: dict[str, Any]) -> None:
        plugin = ScoreboardPlugin(plugin_config)
        game_info = FakeGameInfo(home_team="Eagles", away_team="Hawks", sport="hockey")
        context = HookContext(hook=Hook.ON_GAME_INIT, data={"game_info": game_info})

        plugin.on_game_init(context)

        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "15:00"
        assert (output_dir / "home_name.txt").read_text(encoding="utf-8") == "Eagles"
        assert (output_dir / "away_name.txt").read_text(encoding="utf-8") == "Hawks"

    def test_uses_period_length_from_game_info(self, output_dir: Path, plugin_config: dict[str, Any]) -> None:
        plugin = ScoreboardPlugin(plugin_config)
        game_info = FakeGameInfo(home_team="Eagles", away_team="Hawks", sport="hockey", period_length=17)
        context = HookContext(hook=Hook.ON_GAME_INIT, data={"game_info": game_info})

        plugin.on_game_init(context)

        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "17:00"

    def test_game_info_period_length_overrides_profile(
        self, output_dir: Path, plugin_config: dict[str, Any]
    ) -> None:
        plugin = ScoreboardPlugin(plugin_config)
        game_info = FakeGameInfo(home_team="Eagles", away_team="Hawks", sport="hockey", period_length=25)
        home_profile = FakeTeamProfile(team_name="Eagles", period_length=17)
        context = HookContext(
            hook=Hook.ON_GAME_INIT,
            data={"game_info": game_info, "home_profile": home_profile},
        )

        plugin.on_game_init(context)

        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "25:00"

    def test_falls_back_to_profile_period_length(self, output_dir: Path, plugin_config: dict[str, Any]) -> None:
        plugin = ScoreboardPlugin(plugin_config)
        game_info = FakeGameInfo(home_team="Eagles", away_team="Hawks", sport="hockey")
        home_profile = FakeTeamProfile(team_name="Eagles", period_length=17)
        context = HookContext(
            hook=Hook.ON_GAME_INIT,
            data={"game_info": game_info, "home_profile": home_profile},
        )

        plugin.on_game_init(context)

        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "17:00"

    def test_no_profile_uses_sport_clock(self, output_dir: Path, plugin_config: dict[str, Any]) -> None:
        plugin = ScoreboardPlugin(plugin_config)
        game_info = FakeGameInfo(home_team="Eagles", away_team="Hawks", sport="hockey")
        context = HookContext(hook=Hook.ON_GAME_INIT, data={"game_info": game_info})

        plugin.on_game_init(context)

        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "15:00"

    def test_no_writer_logs_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        plugin = ScoreboardPlugin()
        game_info = FakeGameInfo()
        context = HookContext(hook=Hook.ON_GAME_INIT, data={"game_info": game_info})

        with caplog.at_level(logging.WARNING):
            plugin.on_game_init(context)

        assert "output_directory not configured" in caplog.text

    def test_logs_info_on_success(
        self, output_dir: Path, plugin_config: dict[str, Any], caplog: pytest.LogCaptureFixture
    ) -> None:
        plugin = ScoreboardPlugin(plugin_config)
        game_info = FakeGameInfo(sport="hockey")
        context = HookContext(hook=Hook.ON_GAME_INIT, data={"game_info": game_info})

        with caplog.at_level(logging.INFO):
            plugin.on_game_init(context)

        assert "wrote initial game state" in caplog.text
        assert "hockey" in caplog.text

    def test_clears_timestamps_on_init(self, output_dir: Path, plugin_config: dict[str, Any]) -> None:
        output_dir.mkdir(parents=True)
        (output_dir / "timestamps.txt").write_text("0:00:00 Stale Data\n", encoding="utf-8")

        plugin = ScoreboardPlugin(plugin_config)
        game_info = FakeGameInfo(sport="hockey")
        context = HookContext(hook=Hook.ON_GAME_INIT, data={"game_info": game_info})

        plugin.on_game_init(context)

        assert not (output_dir / "timestamps.txt").exists()

    def test_init_then_finish_no_stale_data(
        self, output_dir: Path, game_dir: Path, plugin_config: dict[str, Any], caplog: pytest.LogCaptureFixture
    ) -> None:
        output_dir.mkdir(parents=True)
        (output_dir / "timestamps.txt").write_text("0:00:00 Stale Data\n", encoding="utf-8")

        plugin = ScoreboardPlugin(plugin_config)

        # Init clears timestamps
        game_info = FakeGameInfo(sport="hockey")
        init_context = HookContext(hook=Hook.ON_GAME_INIT, data={"game_info": game_info})
        plugin.on_game_init(init_context)

        # Finish finds nothing
        state = FakeGameState()
        finish_context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        with caplog.at_level(logging.WARNING):
            plugin.on_game_finish(finish_context)

        assert "timestamps.txt not found" in caplog.text
        assert "game_events" not in finish_context.shared


class TestOnGameFinish:
    def test_copies_timestamps_to_game_dir(
        self, output_dir: Path, game_dir: Path, plugin_config: dict[str, Any]
    ) -> None:
        output_dir.mkdir(parents=True)
        timestamps = "0:00:00 Game Start\n0:12:34 Goal: Eagles (1-0)\n"
        (output_dir / "timestamps.txt").write_text(timestamps, encoding="utf-8")

        plugin = ScoreboardPlugin(plugin_config)
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        plugin.on_game_finish(context)

        assert (game_dir / "chapters.txt").read_text(encoding="utf-8") == timestamps

    def test_no_writer_logs_warning(self, game_dir: Path, caplog: pytest.LogCaptureFixture) -> None:
        plugin = ScoreboardPlugin()
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        with caplog.at_level(logging.WARNING):
            plugin.on_game_finish(context)

        assert "output_directory not configured" in caplog.text

    def test_no_timestamps_logs_warning(
        self, output_dir: Path, game_dir: Path, plugin_config: dict[str, Any], caplog: pytest.LogCaptureFixture
    ) -> None:
        output_dir.mkdir(parents=True)
        plugin = ScoreboardPlugin(plugin_config)
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        with caplog.at_level(logging.WARNING):
            plugin.on_game_finish(context)

        assert "timestamps.txt not found" in caplog.text

    def test_logs_info_on_success(
        self, output_dir: Path, game_dir: Path, plugin_config: dict[str, Any], caplog: pytest.LogCaptureFixture
    ) -> None:
        output_dir.mkdir(parents=True)
        (output_dir / "timestamps.txt").write_text("0:00:00 Game Start\n", encoding="utf-8")

        plugin = ScoreboardPlugin(plugin_config)
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        with caplog.at_level(logging.INFO):
            plugin.on_game_finish(context)

        assert "chapters.txt" in caplog.text

    def test_populates_shared_game_events(
        self, output_dir: Path, game_dir: Path, plugin_config: dict[str, Any]
    ) -> None:
        output_dir.mkdir(parents=True)
        timestamps = "0:00:00 Game Start\n0:12:34 Goal: Eagles (1-0)\n0:25:01 Penalty: Hawks #12\n"
        (output_dir / "timestamps.txt").write_text(timestamps, encoding="utf-8")

        plugin = ScoreboardPlugin(plugin_config)
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        plugin.on_game_finish(context)

        assert context.shared["game_events"] == [
            {"timestamp": "0:00:00", "description": "Game Start"},
            {"timestamp": "0:12:34", "description": "Goal: Eagles (1-0)"},
            {"timestamp": "0:25:01", "description": "Penalty: Hawks #12"},
        ]

    def test_no_timestamps_does_not_set_shared(
        self, output_dir: Path, game_dir: Path, plugin_config: dict[str, Any]
    ) -> None:
        output_dir.mkdir(parents=True)
        plugin = ScoreboardPlugin(plugin_config)
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        plugin.on_game_finish(context)

        assert "game_events" not in context.shared

    def test_unparseable_timestamps_does_not_set_shared(
        self, output_dir: Path, game_dir: Path, plugin_config: dict[str, Any]
    ) -> None:
        output_dir.mkdir(parents=True)
        (output_dir / "timestamps.txt").write_text("no timestamps here\njust text\n", encoding="utf-8")

        plugin = ScoreboardPlugin(plugin_config)
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        plugin.on_game_finish(context)

        assert "game_events" not in context.shared

    def test_no_writer_does_not_set_shared(self, game_dir: Path) -> None:
        plugin = ScoreboardPlugin()
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        plugin.on_game_finish(context)

        assert "game_events" not in context.shared

    def test_populates_shared_scores(
        self, output_dir: Path, game_dir: Path, plugin_config: dict[str, Any]
    ) -> None:
        output_dir.mkdir(parents=True)
        (output_dir / "home_score.txt").write_text("3", encoding="utf-8")
        (output_dir / "away_score.txt").write_text("1", encoding="utf-8")
        (output_dir / "timestamps.txt").write_text("0:00:00 Game Start\n", encoding="utf-8")

        plugin = ScoreboardPlugin(plugin_config)
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        plugin.on_game_finish(context)

        assert context.shared["home_score"] == "3"
        assert context.shared["away_score"] == "1"

    def test_scores_populated_even_without_timestamps(
        self, output_dir: Path, game_dir: Path, plugin_config: dict[str, Any]
    ) -> None:
        output_dir.mkdir(parents=True)
        (output_dir / "home_score.txt").write_text("5", encoding="utf-8")
        (output_dir / "away_score.txt").write_text("2", encoding="utf-8")

        plugin = ScoreboardPlugin(plugin_config)
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        plugin.on_game_finish(context)

        assert context.shared["home_score"] == "5"
        assert context.shared["away_score"] == "2"
        assert "game_events" not in context.shared

    def test_missing_scores_not_in_shared(
        self, output_dir: Path, game_dir: Path, plugin_config: dict[str, Any]
    ) -> None:
        output_dir.mkdir(parents=True)
        (output_dir / "timestamps.txt").write_text("0:00:00 Game Start\n", encoding="utf-8")

        plugin = ScoreboardPlugin(plugin_config)
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        plugin.on_game_finish(context)

        assert "home_score" not in context.shared
        assert "away_score" not in context.shared

    def test_no_writer_does_not_set_scores(self, game_dir: Path) -> None:
        plugin = ScoreboardPlugin()
        state = FakeGameState()
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )

        plugin.on_game_finish(context)

        assert "home_score" not in context.shared
        assert "away_score" not in context.shared


class TestIntegrationWithRegistry:
    def test_full_lifecycle(self, output_dir: Path, plugin_config: dict[str, Any]) -> None:
        """Simulate the full plugin lifecycle: init → register → emit."""
        plugin = ScoreboardPlugin(plugin_config)
        registry = HookRegistry()
        plugin.register(registry)

        game_info = FakeGameInfo(home_team="Storm", away_team="Thunder", sport="basketball")
        context = HookContext(hook=Hook.ON_GAME_INIT, data={"game_info": game_info})
        registry.emit(Hook.ON_GAME_INIT, context)

        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "8:00"
        assert (output_dir / "home_name.txt").read_text(encoding="utf-8") == "Storm"
        assert (output_dir / "away_name.txt").read_text(encoding="utf-8") == "Thunder"
        assert (output_dir / "home_score.txt").read_text(encoding="utf-8") == "0"
        assert (output_dir / "period.txt").read_text(encoding="utf-8") == "1"
        assert (output_dir / "sport.txt").read_text(encoding="utf-8") == "basketball"
        assert (output_dir / "home_fouls.txt").read_text(encoding="utf-8") == "0"

    def test_finish_lifecycle(self, output_dir: Path, game_dir: Path, plugin_config: dict[str, Any]) -> None:
        """Simulate the full plugin lifecycle: init → register → emit finish."""
        plugin = ScoreboardPlugin(plugin_config)
        registry = HookRegistry()
        plugin.register(registry)

        # Simulate OBS writing timestamps during the game
        output_dir.mkdir(parents=True)
        timestamps = "0:00:00 Game Start\n0:12:34 Goal: Storm (1-0)\n"
        (output_dir / "timestamps.txt").write_text(timestamps, encoding="utf-8")

        state = FakeGameState(game_info=FakeGameInfo(home_team="Storm", away_team="Thunder"))
        context = HookContext(
            hook=Hook.ON_GAME_FINISH,
            data={"game_dir": game_dir, "state": state},
        )
        registry.emit(Hook.ON_GAME_FINISH, context)

        assert (game_dir / "chapters.txt").read_text(encoding="utf-8") == timestamps
        assert context.shared["game_events"] == [
            {"timestamp": "0:00:00", "description": "Game Start"},
            {"timestamp": "0:12:34", "description": "Goal: Storm (1-0)"},
        ]
