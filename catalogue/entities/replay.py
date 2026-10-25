from collections.abc import Mapping
from dataclasses import dataclass

from catalogue.entities.timeline import DriverTimeline
from catalogue.entities.units import Distance, LapNumber, Milliseconds, Position

PIT_BOX_BEFORE_LINE = 0.03
MIN_DRIVING_MS = 1000


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


def driver_keyframes(
    driver: DriverTimeline, pit_stops: Mapping[LapNumber, Milliseconds | None]
) -> tuple[Keyframe, ...]:
    frames = [Keyframe(Milliseconds(0), Distance(0.0), untimed_pit(pit_stops, LapNumber(1)))]
    for lap in range(1, driver.laps + 1):
        lap_number = LapNumber(lap)
        crossing = driver.crossings[lap - 1]
        duration = pit_stops.get(lap_number)
        if duration is not None:
            stop_ms = min(duration, driver.lap_time(lap_number) - MIN_DRIVING_MS)
            box = Distance(round(lap - PIT_BOX_BEFORE_LINE, 2))
            frames.append(Keyframe(Milliseconds(crossing - stop_ms), box, True))
            frames.append(Keyframe(crossing, box, True))
        frames.append(
            Keyframe(crossing, Distance(float(lap)), untimed_pit(pit_stops, LapNumber(lap + 1)))
        )
    return tuple(frames)


def untimed_pit(pit_stops: Mapping[LapNumber, Milliseconds | None], lap: LapNumber) -> bool:
    return lap in pit_stops and pit_stops[lap] is None
