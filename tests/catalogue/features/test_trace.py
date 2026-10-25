from catalogue.entities.fastest_lap import FastestLap
from catalogue.entities.trace import DriverTrace
from catalogue.entities.units import (
    LapNumber,
    Milliseconds,
    Position,
    RoundNumber,
    Season,
)
from catalogue.features.trace import Trace, build_trace

from tests.catalogue.fakes import MemorySource


def test_trace_reports_total_laps_fastest_lap_and_series() -> None:
    trace = build_trace(MemorySource(), Season(2025), RoundNumber(1))

    assert trace == Trace(
        Season(2025),
        RoundNumber(1),
        LapNumber(2),
        Milliseconds(207652),
        (
            FastestLap("norris", LapNumber(1), Milliseconds(117099)),
            FastestLap("piastri", LapNumber(2), Milliseconds(90000)),
        ),
        (
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
            DriverTrace("hadjar", "HAD", "rb", Position(11), False, (), (), (), ()),
        ),
    )
