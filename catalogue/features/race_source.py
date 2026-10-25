from typing import Protocol

from catalogue.entities.race_snapshot import LapRow, PitStopRow, ResultRow
from catalogue.entities.units import RoundNumber, Season


class RaceSource(Protocol):
    def laps_of(self, season: Season, round_number: RoundNumber) -> tuple[LapRow, ...]: ...

    def results_of(self, season: Season, round_number: RoundNumber) -> tuple[ResultRow, ...]: ...

    def pit_stops_of(self, season: Season, round_number: RoundNumber) -> tuple[PitStopRow, ...]: ...
