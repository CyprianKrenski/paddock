from collections.abc import Collection
from dataclasses import dataclass

from catalogue.entities.timeline import RaceTimeline
from catalogue.entities.units import LapNumber, Milliseconds


@dataclass(frozen=True, slots=True)
class FastestLap:
    driver_id: str
    lap: LapNumber
    time_ms: Milliseconds


@dataclass(frozen=True, slots=True)
class FastestLapEvent:
    at_ms: Milliseconds
    driver_id: str
    lap: LapNumber
    time_ms: Milliseconds

    @property
    def fastest(self) -> FastestLap:
        return FastestLap(self.driver_id, self.lap, self.time_ms)


def fastest_lap_events(timeline: RaceTimeline) -> tuple[FastestLapEvent, ...]:
    laps = sorted(
        (
            FastestLapEvent(
                driver.crossings[lap - 1],
                driver.driver_id,
                LapNumber(lap),
                driver.lap_time(LapNumber(lap)),
            )
            for driver in timeline.drivers
            for lap in range(1, driver.laps + 1)
        ),
        key=lambda event: (event.at_ms, event.time_ms),
    )
    events: list[FastestLapEvent] = []
    for event in laps:
        if not events or event.time_ms < events[-1].time_ms:
            events.append(event)
    return tuple(events)


def fastest_by_lap(
    timeline: RaceTimeline, eligible: Collection[str] | None = None
) -> tuple[FastestLap, ...]:
    events = [
        event
        for event in fastest_lap_events(timeline)
        if eligible is None or event.driver_id in eligible
    ]
    progression: list[FastestLap] = []
    for lap in range(1, timeline.total_laps + 1):
        completed = max(
            driver.crossings[lap - 1] for driver in timeline.drivers if driver.laps >= lap
        )
        progression.append([event for event in events if event.at_ms <= completed][-1].fastest)
    return tuple(progression)
