from dataclasses import replace

from web.entities.standings import StandingRow, Standings, race_time_text, standings_at
from web.entities.units import LapNumber, Milliseconds, Position
from web.entities.views import DriverTrace

from tests.web.fakes import TRACE

HADJAR = DriverTrace("hadjar", "HAD", "rb", Position(11), False, (), (), (), ())
LAWSON = DriverTrace(
    "lawson",
    None,
    "red_bull",
    Position(0),
    False,
    (Position(3),),
    (Milliseconds(2500),),
    (0,),
    (LapNumber(1),),
)
LAPPED = DriverTrace(
    "stroll",
    "STR",
    "aston_martin",
    Position(9),
    True,
    (Position(4),),
    (Milliseconds(120_000),),
    (1,),
    (),
)
RACE = replace(TRACE, series=TRACE.series + (HADJAR, LAWSON, LAPPED))


def test_running_drivers_by_position_then_retired_by_laps_completed() -> None:
    assert standings_at(RACE, LapNumber(2)) == Standings(
        LapNumber(2),
        (
            StandingRow(
                1, "norris", "NOR", "McLaren", "#ff8000", False, "3:27.652", False, False, False, 1
            ),
            StandingRow(
                2, "piastri", "PIA", "McLaren", "#ff8000", True, "+0.348", False, True, True, -1
            ),
            StandingRow(
                3,
                "stroll",
                "STR",
                "Aston Martin",
                "#229971",
                False,
                "+1 Lap",
                False,
                False,
                False,
                6,
            ),
            StandingRow(
                4, "lawson", "LAW", "Red Bull", "#3671c6", False, "Out", True, False, False, 1
            ),
            StandingRow(5, "hadjar", "HAD", "RB", "#6692ff", False, "Out", True, False, False, 6),
        ),
    )


def test_lapped_drivers_show_laps_down_and_the_fastest_lap_so_far_is_marked() -> None:
    rows = standings_at(RACE, LapNumber(1)).rows

    assert [(row.code, row.cell, row.fastest, row.in_pit) for row in rows] == [
        ("NOR", "LAP 1", True, False),
        ("PIA", "+0.901", False, False),
        ("LAW", "+2.500", False, True),
        ("STR", "+1 Lap", False, False),
        ("HAD", "Out", False, False),
    ]


def test_the_start_follows_the_grid_with_pit_lane_starters_last() -> None:
    rows = standings_at(RACE, LapNumber(0)).rows

    assert [(row.code, row.cell) for row in rows] == [
        ("PIA", "START"),
        ("NOR", ""),
        ("STR", ""),
        ("HAD", ""),
        ("LAW", ""),
    ]


def test_lap_is_clamped_to_the_race_distance() -> None:
    assert standings_at(RACE, LapNumber(9)).lap == 2
    assert standings_at(RACE, LapNumber(-1)).lap == 0


def test_race_time_is_formatted_with_hours_only_when_needed() -> None:
    assert race_time_text(Milliseconds(207652)) == "3:27.652"
    assert race_time_text(Milliseconds(6_126_304)) == "1:42:06.304"


def test_a_disqualified_driver_is_listed_before_retirements_without_points() -> None:
    dsq = replace(TRACE.series[1], classified=False)
    trace = replace(TRACE, series=(TRACE.series[0], dsq, HADJAR))

    rows = standings_at(trace, LapNumber(2)).rows

    assert [(row.code, row.cell, row.out, row.fastest) for row in rows] == [
        ("NOR", "3:27.652", False, False),
        ("PIA", "DSQ", True, False),
        ("HAD", "Out", True, False),
    ]
    assert [(row.code, row.cell) for row in standings_at(trace, LapNumber(1)).rows[:2]] == [
        ("NOR", "LAP 1"),
        ("PIA", "+0.901"),
    ]
