from analysis.entities.rows import LapRow, PitStopRow, ResultRow
from analysis.entities.units import LapNumber, Milliseconds, Position, RoundNumber, Season

NORRIS = (
    LapRow("norris", LapNumber(1), Position(1), Milliseconds(117099)),
    LapRow("norris", LapNumber(2), Position(1), Milliseconds(90553)),
)
PIASTRI = (
    LapRow("piastri", LapNumber(1), Position(2), Milliseconds(118000)),
    LapRow("piastri", LapNumber(2), Position(2), Milliseconds(90000)),
)
RESULTS = (
    ResultRow("norris", "NOR", "mclaren", Position(1), Position(1), LapNumber(2), "Finished"),
    ResultRow("piastri", "PIA", "mclaren", Position(2), Position(2), LapNumber(2), "Finished"),
    ResultRow("hadjar", "HAD", "rb", Position(20), Position(11), LapNumber(0), "Retired"),
)

PIT_STOPS = (PitStopRow("piastri", 1, LapNumber(2), Milliseconds(13341)),)


class MemorySource:
    def __init__(
        self, laps: tuple[LapRow, ...] = NORRIS + PIASTRI, results: tuple[ResultRow, ...] = RESULTS
    ) -> None:
        self._laps = laps
        self._results = results
        self._pit_stops = PIT_STOPS

    def laps_of(self, season: Season, round_number: RoundNumber) -> tuple[LapRow, ...]:
        return self._laps

    def results_of(self, season: Season, round_number: RoundNumber) -> tuple[ResultRow, ...]:
        return self._results

    def pit_stops_of(self, season: Season, round_number: RoundNumber) -> tuple[PitStopRow, ...]:
        return self._pit_stops
