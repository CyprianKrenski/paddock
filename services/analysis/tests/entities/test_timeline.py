from analysis.entities.rows import LapRow
from analysis.entities.timeline import DriverTimeline, RaceTimeline
from analysis.entities.units import LapNumber, Milliseconds, Position

from analysis_tests.fakes import NORRIS, PIASTRI


def test_crossings_are_cumulative_times_per_driver() -> None:
    timeline = RaceTimeline.from_laps(NORRIS + PIASTRI)

    assert timeline.drivers == (
        DriverTimeline(
            "norris", (Milliseconds(117099), Milliseconds(207652)), (Position(1), Position(1))
        ),
        DriverTimeline(
            "piastri", (Milliseconds(118000), Milliseconds(208000)), (Position(2), Position(2))
        ),
    )
    assert timeline.leader_crossing(LapNumber(1)) == 117099
    assert timeline.leader_crossing(LapNumber(2)) == 207652


def test_series_stops_at_the_first_missing_lap_time() -> None:
    rows = (
        LapRow("x", LapNumber(1), Position(1), Milliseconds(100)),
        LapRow("x", LapNumber(2), Position(1), None),
        LapRow("x", LapNumber(3), Position(1), Milliseconds(100)),
    )

    assert RaceTimeline.from_laps(rows).drivers == (
        DriverTimeline("x", (Milliseconds(100),), (Position(1),)),
    )
