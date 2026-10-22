from dataclasses import replace

from web.entities.championship import ChampionshipRow, championship_at
from web.entities.points import fastest_lap_bonus, points_for
from web.entities.units import LapNumber, Position, Season
from web.entities.views import DriverTrace, StandingBefore

from web_tests.fakes import TRACE

HADJAR = DriverTrace("hadjar", "HAD", "rb", Position(11), False, (), (), (), ())
RACE = replace(TRACE, series=TRACE.series + (HADJAR,))
BEFORE = (
    StandingBefore("hadjar", Position(1), 30.0, 1),
    StandingBefore("norris", Position(2), 25.0, 1),
    StandingBefore("piastri", Position(3), 18.0, 0),
    StandingBefore("lawson", Position(4), 12.0, 0),
)
TIED = (
    StandingBefore("piastri", Position(1), 25.0, 1),
    StandingBefore("norris", Position(2), 18.0, 0),
)


def test_points_schemes_by_season() -> None:
    assert [points_for(Season(2025), rank) for rank in (1, 2, 10, 11)] == [25, 18, 1, 0]
    assert [points_for(Season(2005), rank) for rank in (1, 8, 9)] == [10, 1, 0]
    assert [points_for(Season(1995), rank) for rank in (1, 6, 7)] == [10, 1, 0]
    assert [points_for(Season(1975), rank) for rank in (1, 6)] == [9, 1]
    assert [points_for(Season(1955), rank) for rank in (1, 5, 6)] == [8, 2, 0]
    assert (fastest_lap_bonus(Season(2021), 10), fastest_lap_bonus(Season(2021), 11)) == (1, 0)
    assert (fastest_lap_bonus(Season(2025), 1), fastest_lap_bonus(Season(2018), 1)) == (0, 0)


def test_projection_adds_race_points_to_the_standings_before_the_race() -> None:
    assert championship_at(RACE, BEFORE, LapNumber(2)) == (
        ChampionshipRow(1, "NOR", "McLaren", "#ff8000", False, 50.0, 25, 1),
        ChampionshipRow(2, "PIA", "McLaren", "#ff8000", True, 36.0, 18, 1),
        ChampionshipRow(3, "HAD", "RB", "#6692ff", False, 30.0, 0, -2),
        ChampionshipRow(4, "LAW", "", "#555", False, 12.0, 0, 0),
    )


def test_ties_are_broken_by_wins_then_previous_position() -> None:
    rows = championship_at(RACE, TIED, LapNumber(2))

    assert [(row.code, row.points, row.delta) for row in rows[:2]] == [
        ("PIA", 43.0, 0),
        ("NOR", 43.0, 0),
    ]


def test_before_the_start_nobody_scores_and_newcomers_have_no_delta() -> None:
    rows = championship_at(RACE, (), LapNumber(0))

    assert [(row.code, row.points, row.gained, row.delta) for row in rows] == [
        ("NOR", 0.0, 0, None),
        ("PIA", 0.0, 0, None),
        ("HAD", 0.0, 0, None),
    ]
