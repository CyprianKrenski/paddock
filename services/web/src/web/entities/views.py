from dataclasses import dataclass
from datetime import date

from web.entities.units import Distance, LapNumber, Milliseconds, Position, RoundNumber, Season


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
    grid: Position | None
    classified: bool
    positions: tuple[Position, ...]
    gaps_ms: tuple[Milliseconds, ...]
    laps_down: tuple[int, ...]
    pit_laps: tuple[LapNumber, ...]

    @property
    def label(self) -> str:
        return self.code or self.driver_id[:3].upper()


@dataclass(frozen=True, slots=True)
class Trace:
    season: Season
    round_number: RoundNumber
    total_laps: LapNumber
    race_time_ms: Milliseconds | None
    fastest_by_lap: tuple[FastestLap, ...]
    series: tuple[DriverTrace, ...]

    @property
    def fastest_lap(self) -> FastestLap | None:
        return self.fastest_by_lap[-1] if self.fastest_by_lap else None


@dataclass(frozen=True, slots=True)
class Keyframe:
    at_ms: Milliseconds
    distance: Distance
    in_pit: bool


@dataclass(frozen=True, slots=True)
class DriverReplay:
    driver_id: str
    code: str | None
    team: str | None
    grid: Position | None
    classified: bool
    keyframes: tuple[Keyframe, ...]

    @property
    def label(self) -> str:
        return self.code or self.driver_id[:3].upper()


@dataclass(frozen=True, slots=True)
class FastestLapEvent:
    at_ms: Milliseconds
    driver_id: str
    lap: LapNumber
    time_ms: Milliseconds


@dataclass(frozen=True, slots=True)
class Replay:
    season: Season
    round_number: RoundNumber
    total_laps: LapNumber
    fastest_laps: tuple[FastestLapEvent, ...]
    drivers: tuple[DriverReplay, ...]


@dataclass(frozen=True, slots=True)
class StandingBefore:
    driver_id: str
    position: Position
    points: float
    wins: int
