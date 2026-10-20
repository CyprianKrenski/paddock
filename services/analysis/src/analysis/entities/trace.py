from dataclasses import dataclass

from analysis.entities.timeline import RaceTimeline
from analysis.entities.units import LapNumber, Milliseconds


@dataclass(frozen=True, slots=True)
class DriverTrace:
    driver_id: str
    gaps_ms: tuple[Milliseconds, ...]


def race_trace(timeline: RaceTimeline) -> tuple[DriverTrace, ...]:
    return tuple(
        DriverTrace(
            driver.driver_id,
            tuple(
                Milliseconds(crossing - timeline.leader_crossing(LapNumber(lap)))
                for lap, crossing in enumerate(driver.crossings, start=1)
            ),
        )
        for driver in timeline.drivers
    )
