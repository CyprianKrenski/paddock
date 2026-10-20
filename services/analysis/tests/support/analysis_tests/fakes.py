from analysis.entities.rows import LapRow, ResultRow
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
    ResultRow("norris", Position(1), Position(1), LapNumber(2), "Finished"),
    ResultRow("piastri", Position(2), Position(2), LapNumber(2), "Finished"),
    ResultRow("hadjar", Position(20), Position(11), LapNumber(0), "Retired"),
)


class MemorySource:
    def __init__(
        self, laps: tuple[LapRow, ...] = NORRIS + PIASTRI, results: tuple[ResultRow, ...] = RESULTS
    ) -> None:
        self._laps = laps
        self._results = results

    def laps_of(self, season: Season, round_number: RoundNumber) -> tuple[LapRow, ...]:
        return self._laps

    def results_of(self, season: Season, round_number: RoundNumber) -> tuple[ResultRow, ...]:
        return self._results
