"""Tests for plugin module."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pytest
from reeln.plugins.hooks import Hook, HookContext
from reeln.plugins.registry import HookRegistry

from streamn_scoreboard_plugin.plugin import ScoreboardPlugin
from tests.conftest import FakeGameInfo, FakeTeamProfile


class TestScoreboardPluginAttributes:
    def test_name(self) -> None:
        plugin = ScoreboardPlugin()
        assert plugin.name == "streamn-scoreboard"

    def test_version(self) -> None:
        plugin = ScoreboardPlugin()
        assert plugin.version == "0.3.0"

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

    def test_does_not_register_other_hooks(self) -> None:
        plugin = ScoreboardPlugin()
        registry = HookRegistry()
        plugin.register(registry)
        assert not registry.has_handlers(Hook.ON_GAME_FINISH)


class TestOnGameInit:
    def test_writes_files_on_hook(self, output_dir: Path, plugin_config: dict[str, Any]) -> None:
        plugin = ScoreboardPlugin(plugin_config)
        game_info = FakeGameInfo(home_team="Eagles", away_team="Hawks", sport="hockey")
        context = HookContext(hook=Hook.ON_GAME_INIT, data={"game_info": game_info})

        plugin.on_game_init(context)

        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "20:00"
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

        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "20:00"

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


class TestIntegrationWithRegistry:
    def test_full_lifecycle(self, output_dir: Path, plugin_config: dict[str, Any]) -> None:
        """Simulate the full plugin lifecycle: init → register → emit."""
        plugin = ScoreboardPlugin(plugin_config)
        registry = HookRegistry()
        plugin.register(registry)

        game_info = FakeGameInfo(home_team="Storm", away_team="Thunder", sport="basketball")
        context = HookContext(hook=Hook.ON_GAME_INIT, data={"game_info": game_info})
        registry.emit(Hook.ON_GAME_INIT, context)

        assert (output_dir / "clock.txt").read_text(encoding="utf-8") == "12:00"
        assert (output_dir / "home_name.txt").read_text(encoding="utf-8") == "Storm"
        assert (output_dir / "away_name.txt").read_text(encoding="utf-8") == "Thunder"
        assert (output_dir / "home_score.txt").read_text(encoding="utf-8") == "0"
        assert (output_dir / "period.txt").read_text(encoding="utf-8") == "1"
        assert (output_dir / "sport.txt").read_text(encoding="utf-8") == "basketball"
        assert (output_dir / "home_fouls.txt").read_text(encoding="utf-8") == "0"
