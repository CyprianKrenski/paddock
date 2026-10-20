from dataclasses import dataclass
from datetime import date

from catalogue.entities.lap_time import LapTimeMs
from catalogue.entities.units import LapNumber, Position, RoundNumber, Season


@dataclass(frozen=True, slots=True)
class RaceInfo:
    season: Season
    round_number: RoundNumber
    name: str
    circuit_id: str
    circuit_name: str
    date: date
    total_laps: LapNumber | None


@dataclass(frozen=True, slots=True)
class DriverInfo:
    id: str
    code: str | None
    given_name: str
    family_name: str


@dataclass(frozen=True, slots=True)
class ResultRow:
    driver_id: str
    code: str | None
    constructor_id: str | None
    position: Position | None
    grid: Position
    laps: LapNumber
    status: str


@dataclass(frozen=True, slots=True)
class LapRow:
    driver_id: str
    lap: LapNumber
    position: Position
    time_ms: LapTimeMs | None


@dataclass(frozen=True, slots=True)
class PitStopRow:
    driver_id: str
    stop: int
    lap: LapNumber
    duration_ms: LapTimeMs | None


@dataclass(frozen=True, slots=True)
class RaceSnapshot:
    race: RaceInfo
    drivers: tuple[DriverInfo, ...]
    results: tuple[ResultRow, ...]
    laps: tuple[LapRow, ...]
    pit_stops: tuple[PitStopRow, ...]


@dataclass(frozen=True, slots=True)
class RaceSummary:
    season: Season
    round_number: RoundNumber
    name: str
    circuit_name: str
    date: date
    ingested: bool
