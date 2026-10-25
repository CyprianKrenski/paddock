from catalogue.entities.fastest_lap import (
    FastestLap,
    FastestLapEvent,
    fastest_by_lap,
    fastest_lap_events,
)
from catalogue.entities.race_snapshot import LapRow
from catalogue.entities.timeline import RaceTimeline
from catalogue.entities.units import LapNumber, Milliseconds, Position

from tests.catalogue.fakes import NORRIS, PIASTRI

TIMELINE = RaceTimeline.from_laps(NORRIS + PIASTRI)


def test_no_laps_means_no_fastest_lap() -> None:
    assert fastest_by_lap(RaceTimeline.from_laps(())) == ()
    assert fastest_lap_events(RaceTimeline.from_laps(())) == ()


def test_fastest_lap_so_far_after_each_lap() -> None:
    assert fastest_by_lap(TIMELINE) == (
        FastestLap("norris", lap=LapNumber(1), time_ms=Milliseconds(117099)),
        FastestLap("piastri", lap=LapNumber(2), time_ms=Milliseconds(90000)),
    )


def test_fastest_lap_events_are_the_moments_the_record_improves() -> None:
    assert fastest_lap_events(TIMELINE) == (
        FastestLapEvent(Milliseconds(117099), "norris", LapNumber(1), Milliseconds(117099)),
        FastestLapEvent(Milliseconds(207652), "norris", LapNumber(2), Milliseconds(90553)),
        FastestLapEvent(Milliseconds(208000), "piastri", LapNumber(2), Milliseconds(90000)),
    )


def test_ties_go_to_the_driver_who_set_the_time_first() -> None:
    rows = (
        LapRow("late", LapNumber(1), Position(1), Milliseconds(100)),
        LapRow("late", LapNumber(2), Position(1), Milliseconds(50)),
        LapRow("early", LapNumber(1), Position(2), Milliseconds(60)),
        LapRow("early", LapNumber(2), Position(2), Milliseconds(50)),
    )

    assert fastest_by_lap(RaceTimeline.from_laps(rows))[-1] == FastestLap(
        "early", lap=LapNumber(2), time_ms=Milliseconds(50)
    )


def test_disqualified_drivers_do_not_hold_the_fastest_lap_in_the_table() -> None:
    assert fastest_by_lap(TIMELINE, eligible={"norris"}) == (
        FastestLap("norris", lap=LapNumber(1), time_ms=Milliseconds(117099)),
        FastestLap("norris", lap=LapNumber(2), time_ms=Milliseconds(90553)),
    )
