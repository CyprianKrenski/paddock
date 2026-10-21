from analysis.entities.fastest_lap import FastestLap
from analysis.entities.trace import DriverTrace
from analysis.entities.units import (
    DriverStatus,
    LapNumber,
    Milliseconds,
    Position,
    RoundNumber,
    Season,
)
from analysis.features.frame import build_frame
from analysis.features.trace import Trace, build_trace

from analysis_tests.fakes import MemorySource


def test_trace_reports_total_laps_fastest_lap_and_series() -> None:
    trace = build_trace(MemorySource(), Season(2025), RoundNumber(1))

    assert trace == Trace(
        Season(2025),
        RoundNumber(1),
        LapNumber(2),
        FastestLap("piastri", LapNumber(2), Milliseconds(90000)),
        (
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
            DriverTrace("hadjar", "HAD", "rb", (), (), ()),
        ),
    )


def test_frame_converts_seconds_to_milliseconds() -> None:
    frame = build_frame(MemorySource(), Season(2025), RoundNumber(1), at_seconds=200.0)

    assert frame.at_seconds == 200.0
    assert [state.driver_id for state in frame.drivers] == ["norris", "piastri", "hadjar"]
    assert frame.drivers[2].status == DriverStatus.OUT
    assert frame.drivers[1].gap_ms == 395
    assert frame.fastest_lap == FastestLap("norris", LapNumber(1), Milliseconds(117099))
