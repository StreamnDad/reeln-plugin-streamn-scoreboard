"""reeln-cli plugin that bridges game init to OBS scoreboard text files."""

from __future__ import annotations

__version__ = "0.3.0"

from streamn_scoreboard_plugin.plugin import ScoreboardPlugin

__all__ = ["ScoreboardPlugin", "__version__"]
