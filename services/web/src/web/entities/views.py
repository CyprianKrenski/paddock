from dataclasses import dataclass
from datetime import date

from web.entities.units import LapNumber, Milliseconds, Position, RoundNumber, Season


@dataclass(frozen=True, slots=True)
class RaceSummary:
    season: Season
    round_number: RoundNumber
    name: str
    circuit_name: str
    date: date
    ingested: bool


@dataclass(frozen=True, slots=True)
class FastestLap:
    driver_id: str
    lap: LapNumber
    time_ms: Milliseconds


@dataclass(frozen=True, slots=True)
class DriverTrace:
    driver_id: str
    code: str | None
    team: str | None
    positions: tuple[Position, ...]
    gaps_ms: tuple[Milliseconds, ...]
    pit_laps: tuple[LapNumber, ...]


@dataclass(frozen=True, slots=True)
class Trace:
    season: Season
    round_number: RoundNumber
    total_laps: LapNumber
    fastest_lap: FastestLap | None
    series: tuple[DriverTrace, ...]
