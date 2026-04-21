"""reeln-cli plugin that bridges game lifecycle to OBS scoreboard text files."""

from __future__ import annotations

__version__ = "0.6.0"

from streamn_scoreboard_plugin.plugin import ScoreboardPlugin

__all__ = ["ScoreboardPlugin", "__version__"]
