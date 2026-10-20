from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from analysis.entities.rows import PitStopRow, ResultRow
from analysis.entities.timeline import RaceTimeline
from analysis.entities.units import LapNumber, Milliseconds, Position


@dataclass(frozen=True, slots=True)
class DriverTrace:
    driver_id: str
    code: str | None
    team: str | None
    positions: tuple[Position, ...]
    gaps_ms: tuple[Milliseconds, ...]
    pit_laps: tuple[LapNumber, ...]


def race_trace(
    timeline: RaceTimeline, results: Mapping[str, ResultRow], pit_stops: Iterable[PitStopRow]
) -> tuple[DriverTrace, ...]:
    pits: dict[str, list[LapNumber]] = {}
    for stop in pit_stops:
        pits.setdefault(stop.driver_id, []).append(stop.lap)
    return tuple(
        DriverTrace(
            driver.driver_id,
            results[driver.driver_id].code if driver.driver_id in results else None,
            results[driver.driver_id].constructor_id if driver.driver_id in results else None,
            driver.positions,
            tuple(
                Milliseconds(crossing - timeline.leader_crossing(LapNumber(lap)))
                for lap, crossing in enumerate(driver.crossings, start=1)
            ),
            tuple(sorted(lap for lap in pits.get(driver.driver_id, ()) if lap <= driver.laps)),
        )
        for driver in timeline.drivers
    )
