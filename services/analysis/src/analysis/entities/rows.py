from dataclasses import dataclass

from analysis.entities.units import LapNumber, Milliseconds, Position


@dataclass(frozen=True, slots=True)
class LapRow:
    driver_id: str
    lap: LapNumber
    position: Position
    time_ms: Milliseconds | None


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
class PitStopRow:
    driver_id: str
    stop: int
    lap: LapNumber
    duration_ms: Milliseconds | None
