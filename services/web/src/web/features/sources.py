from typing import Protocol

from web.entities.json_object import JsonObject
from web.entities.units import RoundNumber, Season
from web.entities.views import RaceSummary, Trace


class Catalogue(Protocol):
    def seasons(self) -> tuple[Season, ...]: ...

    def races_of(self, season: Season) -> tuple[RaceSummary, ...]: ...

    def load_season(self, season: Season) -> None: ...

    def load_race(self, season: Season, round_number: RoundNumber) -> None: ...


class Analysis(Protocol):
    def trace_of(self, season: Season, round_number: RoundNumber) -> Trace: ...

    def frame_of(
        self, season: Season, round_number: RoundNumber, at_seconds: float
    ) -> JsonObject: ...
