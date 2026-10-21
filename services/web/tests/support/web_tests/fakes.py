from datetime import date

from web.entities.json_object import JsonObject
from web.entities.units import LapNumber, Milliseconds, Position, RoundNumber, Season
from web.entities.views import DriverTrace, FastestLap, RaceSummary, Trace

AUSTRALIA = RaceSummary(
    Season(2025), RoundNumber(1), "Australian Grand Prix", "Albert Park", date(2025, 3, 16), True
)
CHINA = RaceSummary(
    Season(2025), RoundNumber(2), "Chinese Grand Prix", "Shanghai", date(2025, 3, 23), False
)
TRACE = Trace(
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
            Position(2),
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
            Position(1),
            True,
            (Position(2), Position(2)),
            (Milliseconds(901), Milliseconds(348)),
            (0, 0),
            (LapNumber(2),),
        ),
    ),
)


class MemoryCatalogue:
    def __init__(self) -> None:
        self.loaded: list[tuple[Season, RoundNumber | None]] = []

    def seasons(self) -> tuple[Season, ...]:
        return (Season(2025),)

    def races_of(self, season: Season) -> tuple[RaceSummary, ...]:
        return (AUSTRALIA, CHINA) if season == 2025 else ()

    def load_season(self, season: Season) -> None:
        self.loaded.append((season, None))

    def load_race(self, season: Season, round_number: RoundNumber) -> None:
        self.loaded.append((season, round_number))


class MemoryAnalysis:
    def trace_of(self, season: Season, round_number: RoundNumber) -> Trace:
        return TRACE

    def frame_of(self, season: Season, round_number: RoundNumber, at_seconds: float) -> JsonObject:
        return {"at_seconds": at_seconds, "drivers": []}
