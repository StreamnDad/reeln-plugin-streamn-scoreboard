"""Tests for sport_mapping module."""

from __future__ import annotations

import pytest

from streamn_scoreboard_plugin.sport_mapping import (
    format_clock,
    get_clock_for_sport,
    get_default_period_labels,
    get_game_init_values,
)
from tests.conftest import FakeGameInfo


class TestFormatClock:
    def test_none_returns_zero(self) -> None:
        assert format_clock(None) == "0:00"

    def test_twenty_minutes(self) -> None:
        assert format_clock(20) == "20:00"

    def test_twelve_minutes(self) -> None:
        assert format_clock(12) == "12:00"

    def test_forty_five_minutes(self) -> None:
        assert format_clock(45) == "45:00"

    def test_zero_minutes(self) -> None:
        assert format_clock(0) == "0:00"


class TestGetClockForSport:
    @pytest.mark.parametrize(
        ("sport", "expected"),
        [
            ("hockey", "15:00"),
            ("basketball", "8:00"),
            ("soccer", "45:00"),
            ("football", "30:00"),
            ("lacrosse", "12:00"),
            ("rugby", "40:00"),
            ("baseball", "0:00"),
            ("generic", "0:00"),
        ],
    )
    def test_known_sports(self, sport: str, expected: str) -> None:
        assert get_clock_for_sport(sport) == expected

    def test_unknown_sport_falls_back(self) -> None:
        assert get_clock_for_sport("curling") == "0:00"


class TestGetGameInitValues:
    def test_hockey_init(self) -> None:
        game_info = FakeGameInfo(home_team="Eagles", away_team="Hawks", sport="hockey")
        values = get_game_init_values(game_info)

        assert values["clock"] == "15:00"
        assert values["period"] == "1"
        assert values["home_name"] == "Eagles"
        assert values["away_name"] == "Hawks"
        assert values["home_score"] == "0"
        assert values["away_score"] == "0"
        assert values["home_shots"] == "0"
        assert values["away_shots"] == "0"
        assert values["home_fouls"] == "0"
        assert values["away_fouls"] == "0"
        assert values["home_fouls2"] == "0"
        assert values["away_fouls2"] == "0"
        assert values["home_penalty_numbers"] == ""
        assert values["home_penalty_times"] == ""
        assert values["away_penalty_numbers"] == ""
        assert values["away_penalty_times"] == ""
        assert values["sport"] == "hockey"
        assert values["home_faceoffs"] == "0"
        assert values["away_faceoffs"] == "0"
        assert values["default_penalty_duration"] == "120"
        assert values["default_major_penalty_duration"] == "300"
        assert values["period_length"] == "900"

    def test_baseball_init(self) -> None:
        game_info = FakeGameInfo(sport="baseball", home_team="Red Sox", away_team="Yankees")
        values = get_game_init_values(game_info)

        assert values["clock"] == "0:00"
        assert values["home_name"] == "Red Sox"
        assert values["away_name"] == "Yankees"

    def test_returns_twenty_three_keys(self) -> None:
        values = get_game_init_values(FakeGameInfo())
        assert len(values) == 23

    def test_baseball_period_length_zero(self) -> None:
        game_info = FakeGameInfo(sport="baseball", home_team="Red Sox", away_team="Yankees")
        values = get_game_init_values(game_info)
        assert values["period_length"] == "0"

    def test_baseball_sport_field(self) -> None:
        game_info = FakeGameInfo(sport="baseball", home_team="Red Sox", away_team="Yankees")
        values = get_game_init_values(game_info)
        assert values["sport"] == "baseball"

    def test_missing_attributes_fallback(self) -> None:
        """Object without expected attributes uses defaults."""

        class Bare:
            pass

        values = get_game_init_values(Bare())
        assert values["clock"] == "0:00"
        assert values["home_name"] == ""
        assert values["away_name"] == ""
        assert values["sport"] == "generic"

    def test_period_length_overrides_sport(self) -> None:
        """Explicit period_length overrides sport-based clock."""
        game_info = FakeGameInfo(sport="hockey")
        values = get_game_init_values(game_info, period_length=17)
        assert values["clock"] == "17:00"
        assert values["period_length"] == "1020"

    def test_period_length_none_falls_back_to_sport(self) -> None:
        """period_length=None uses sport-based clock."""
        game_info = FakeGameInfo(sport="hockey")
        values = get_game_init_values(game_info, period_length=None)
        assert values["clock"] == "15:00"
        assert values["period_length"] == "900"

    def test_hockey_default_period_labels(self) -> None:
        values = get_game_init_values(FakeGameInfo(sport="hockey"))
        assert values["period_labels"] == "1\n2\n3\nOT\nOT2\nOT3\nOT4\n"

    def test_basketball_default_period_labels(self) -> None:
        values = get_game_init_values(FakeGameInfo(sport="basketball"))
        assert values["period_labels"] == "1\n2\n3\n4\nOT\n"

    def test_custom_period_labels_from_game_info(self) -> None:
        game_info = FakeGameInfo(sport="hockey")
        game_info.period_labels = "1\n2\n3\n4\n5\nOT\n2OT\n"
        values = get_game_init_values(game_info)
        assert values["period_labels"] == "1\n2\n3\n4\n5\nOT\n2OT\n"


class TestGetDefaultPeriodLabels:
    def test_hockey(self) -> None:
        assert get_default_period_labels("hockey") == "1\n2\n3\nOT\nOT2\nOT3\nOT4\n"

    def test_basketball(self) -> None:
        assert get_default_period_labels("basketball") == "1\n2\n3\n4\nOT\n"

    def test_soccer(self) -> None:
        assert get_default_period_labels("soccer") == "1\n2\nOT\n"

    def test_baseball(self) -> None:
        assert get_default_period_labels("baseball") == "1\n2\n3\n4\n5\n6\n7\n8\n9\n"

    def test_generic(self) -> None:
        assert get_default_period_labels("generic") == "1\n"

    def test_unknown_sport(self) -> None:
        assert get_default_period_labels("curling") == "1\n"
