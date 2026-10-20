from analysis.entities.timeline import RaceTimeline
from analysis.entities.trace import DriverTrace, race_trace
from analysis.entities.units import Milliseconds

from analysis_tests.fakes import NORRIS, PIASTRI


def test_gap_to_the_leader_on_the_same_lap() -> None:
    assert race_trace(RaceTimeline.from_laps(NORRIS + PIASTRI)) == (
        DriverTrace("norris", (Milliseconds(0), Milliseconds(0))),
        DriverTrace("piastri", (Milliseconds(901), Milliseconds(348))),
    )
