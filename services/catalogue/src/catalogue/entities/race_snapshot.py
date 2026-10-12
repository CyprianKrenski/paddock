from dataclasses import dataclass
from datetime import date

from catalogue.entities.lap_time import LapTimeMs


@dataclass(frozen=True, slots=True)
class RaceInfo:
    season: int
    round_number: int
    name: str
    circuit_id: str
    circuit_name: str
    date: date
    total_laps: int | None


@dataclass(frozen=True, slots=True)
class DriverInfo:
    id: str
    code: str | None
    given_name: str
    family_name: str


@dataclass(frozen=True, slots=True)
class ResultRow:
    driver_id: str
    position: int | None
    grid: int
    laps: int
    status: str


@dataclass(frozen=True, slots=True)
class LapRow:
    driver_id: str
    lap: int
    position: int
    time_ms: LapTimeMs | None


@dataclass(frozen=True, slots=True)
class PitStopRow:
    driver_id: str
    stop: int
    lap: int
    duration_ms: LapTimeMs | None


@dataclass(frozen=True, slots=True)
class RaceSnapshot:
    race: RaceInfo
    drivers: tuple[DriverInfo, ...]
    results: tuple[ResultRow, ...]
    laps: tuple[LapRow, ...]
    pit_stops: tuple[PitStopRow, ...]
