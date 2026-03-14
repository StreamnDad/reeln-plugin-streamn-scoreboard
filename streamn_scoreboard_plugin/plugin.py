"""ScoreboardPlugin — reeln-cli plugin for OBS scoreboard integration."""

from __future__ import annotations

import logging
from typing import Any

from reeln.models.plugin_schema import ConfigField, PluginConfigSchema
from reeln.plugins.hooks import Hook, HookContext
from reeln.plugins.registry import HookRegistry

from streamn_scoreboard_plugin.writer import ScoreboardWriter, parse_timestamps

log: logging.Logger = logging.getLogger(__name__)


class ScoreboardPlugin:
    """Plugin that bridges reeln-cli game lifecycle to OBS scoreboard text files.

    Subscribes to ``ON_GAME_INIT`` (writes initial state to 17 text files and
    clears stale timestamps) and ``ON_GAME_FINISH`` (copies event timestamps
    to the game directory and populates ``context.shared["game_events"]``).
    """

    name: str = "streamn-scoreboard"
    version: str = "0.4.0"
    api_version: int = 1

    config_schema: PluginConfigSchema = PluginConfigSchema(
        fields=(
            ConfigField(
                name="output_directory",
                field_type="str",
                required=True,
                description="Path to the scoreboard text file output directory",
            ),
        )
    )

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config: dict[str, Any] = config or {}
        self._writer: ScoreboardWriter | None = None
        if "output_directory" in self._config:
            self._writer = ScoreboardWriter(self._config["output_directory"])

    def register(self, registry: HookRegistry) -> None:
        """Register hook handlers with the reeln plugin registry."""
        registry.register(Hook.ON_GAME_INIT, self.on_game_init)
        registry.register(Hook.ON_GAME_FINISH, self.on_game_finish)

    def on_game_init(self, context: HookContext) -> None:
        """Handle ``ON_GAME_INIT`` — write initial scoreboard state."""
        if self._writer is None:
            log.warning("Scoreboard plugin: output_directory not configured, skipping write")
            return
        game_info = context.data["game_info"]

        # Resolve period length: game_info.period_length (non-zero) takes
        # precedence, then home_profile.period_length, then sport fallback.
        period_length: int | None = None
        gi_period = getattr(game_info, "period_length", 0)
        if gi_period:
            period_length = gi_period
        else:
            home_profile = context.data.get("home_profile")
            if home_profile is not None:
                period_length = getattr(home_profile, "period_length", None)

        self._writer.write_game_init(game_info, period_length=period_length)
        self._writer.clear_timestamps()
        log.info("Scoreboard plugin: wrote initial game state for %s", getattr(game_info, "sport", "unknown"))

    def on_game_finish(self, context: HookContext) -> None:
        """Handle ``ON_GAME_FINISH`` — copy event timestamps to game directory.

        Also populates ``context.shared["game_events"]`` with parsed
        timestamp entries for downstream plugins (e.g. Google plugin
        YouTube chapter insertion).
        """
        if self._writer is None:
            log.warning("Scoreboard plugin: output_directory not configured, skipping finish")
            return

        game_dir = context.data["game_dir"]
        result = self._writer.write_game_finish(game_dir)
        if result is None:
            return

        log.info("Scoreboard plugin: wrote %s", result)

        content = result.read_text(encoding="utf-8")
        events = parse_timestamps(content)
        if events:
            context.shared["game_events"] = events
