from catalogue.entities.fastest_lap import FastestLapEvent
from catalogue.entities.replay import DriverReplay, Keyframe
from catalogue.entities.units import (
    Distance,
    LapNumber,
    Milliseconds,
    Position,
    RoundNumber,
    Season,
)
from catalogue.features.replay import Replay, build_replay

from tests.catalogue.fakes import MemorySource


def test_replay_has_keyframes_for_every_classified_driver() -> None:
    replay = build_replay(MemorySource(), Season(2025), RoundNumber(1))

    assert replay == Replay(
        Season(2025),
        RoundNumber(1),
        LapNumber(2),
        (
            FastestLapEvent(Milliseconds(117099), "norris", LapNumber(1), Milliseconds(117099)),
            FastestLapEvent(Milliseconds(207652), "norris", LapNumber(2), Milliseconds(90553)),
            FastestLapEvent(Milliseconds(208000), "piastri", LapNumber(2), Milliseconds(90000)),
        ),
        (
            DriverReplay(
                "norris",
                "NOR",
                "mclaren",
                Position(1),
                True,
                (
                    Keyframe(Milliseconds(0), Distance(0.0), False),
                    Keyframe(Milliseconds(117099), Distance(1.0), False),
                    Keyframe(Milliseconds(207652), Distance(2.0), False),
                ),
            ),
            DriverReplay(
                "piastri",
                "PIA",
                "mclaren",
                Position(2),
                True,
                (
                    Keyframe(Milliseconds(0), Distance(0.0), False),
                    Keyframe(Milliseconds(118000), Distance(1.0), False),
                    Keyframe(Milliseconds(194659), Distance(1.97), True),
                    Keyframe(Milliseconds(208000), Distance(1.97), True),
                    Keyframe(Milliseconds(208000), Distance(2.0), False),
                ),
            ),
            DriverReplay(
                "hadjar",
                "HAD",
                "rb",
                Position(11),
                False,
                (Keyframe(Milliseconds(0), Distance(0.0), False),),
            ),
        ),
    )
