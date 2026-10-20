from analysis.entities.timeline import RaceTimeline
from analysis.entities.trace import DriverTrace, race_trace
from analysis.entities.units import LapNumber, Milliseconds, Position

from analysis_tests.fakes import NORRIS, PIASTRI, PIT_STOPS, RESULTS


def test_gap_to_the_leader_on_the_same_lap_with_team_and_pit_laps() -> None:
    results = {row.driver_id: row for row in RESULTS}

    assert race_trace(RaceTimeline.from_laps(NORRIS + PIASTRI), results, PIT_STOPS) == (
        DriverTrace(
            "norris",
            "NOR",
            "mclaren",
            (Position(1), Position(1)),
            (Milliseconds(0), Milliseconds(0)),
            (),
        ),
        DriverTrace(
            "piastri",
            "PIA",
            "mclaren",
            (Position(2), Position(2)),
            (Milliseconds(901), Milliseconds(348)),
            (LapNumber(2),),
        ),
    )
