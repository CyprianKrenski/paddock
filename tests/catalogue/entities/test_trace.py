from catalogue.entities.race_snapshot import LapRow
from catalogue.entities.timeline import RaceTimeline
from catalogue.entities.trace import DriverTrace, race_trace
from catalogue.entities.units import LapNumber, Milliseconds, Position

from tests.catalogue.fakes import NORRIS, PIASTRI, PIT_STOPS, RESULTS


def test_gap_to_the_leader_on_the_same_lap_with_team_and_pit_laps() -> None:
    results = {row.driver_id: row for row in RESULTS}

    assert race_trace(RaceTimeline.from_laps(NORRIS + PIASTRI), results, PIT_STOPS) == (
        DriverTrace(
            "norris",
            "NOR",
            "mclaren",
            Position(1),
            True,
            (Position(1), Position(1)),
            (Milliseconds(0), Milliseconds(0)),
            (0, 0),
            (),
        ),
        DriverTrace(
            "piastri",
            "PIA",
            "mclaren",
            Position(2),
            True,
            (Position(2), Position(2)),
            (Milliseconds(901), Milliseconds(348)),
            (0, 0),
            (LapNumber(2),),
        ),
    )


def test_a_driver_lapped_by_the_leader_counts_laps_down() -> None:
    slow = (LapRow("slow", LapNumber(1), Position(3), Milliseconds(210000)),)
    results = {row.driver_id: row for row in RESULTS}

    trace = race_trace(RaceTimeline.from_laps(NORRIS + PIASTRI + slow), results, ())

    assert trace[2] == DriverTrace(
        "slow", None, None, None, False, (Position(3),), (Milliseconds(92901),), (1,), ()
    )
