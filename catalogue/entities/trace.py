from bisect import bisect_right
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from catalogue.entities.race_snapshot import PitStopRow, ResultRow
from catalogue.entities.timeline import DriverTimeline, RaceTimeline
from catalogue.entities.units import LapNumber, Milliseconds, Position


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


def race_trace(
    timeline: RaceTimeline, results: Mapping[str, ResultRow], pit_stops: Iterable[PitStopRow]
) -> tuple[DriverTrace, ...]:
    pits: dict[str, list[LapNumber]] = {}
    for stop in pit_stops:
        pits.setdefault(stop.driver_id, []).append(stop.lap)
    leaders = timeline.leader_crossings()
    return tuple(
        driver_trace(driver, results.get(driver.driver_id), leaders, pits.get(driver.driver_id, ()))
        for driver in timeline.drivers
    )


def driver_trace(
    driver: DriverTimeline,
    result: ResultRow | None,
    leaders: tuple[Milliseconds, ...],
    pit_laps: Iterable[LapNumber],
) -> DriverTrace:
    return DriverTrace(
        driver.driver_id,
        result.code if result else None,
        result.constructor_id if result else None,
        result.grid if result else None,
        result is not None and result.classified,
        driver.positions,
        tuple(
            Milliseconds(crossing - leaders[lap - 1])
            for lap, crossing in enumerate(driver.crossings, start=1)
        ),
        tuple(
            bisect_right(leaders, crossing) - lap
            for lap, crossing in enumerate(driver.crossings, start=1)
        ),
        tuple(sorted(lap for lap in pit_laps if lap <= driver.laps)),
    )
