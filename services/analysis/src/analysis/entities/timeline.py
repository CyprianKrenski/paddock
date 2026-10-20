from collections.abc import Iterable
from dataclasses import dataclass

from analysis.entities.rows import LapRow
from analysis.entities.units import LapNumber, Milliseconds


@dataclass(frozen=True, slots=True)
class DriverTimeline:
    driver_id: str
    crossings: tuple[Milliseconds, ...]

    @property
    def laps(self) -> LapNumber:
        return LapNumber(len(self.crossings))

    @property
    def last_crossing(self) -> Milliseconds:
        return self.crossings[-1] if self.crossings else Milliseconds(0)


@dataclass(frozen=True, slots=True)
class RaceTimeline:
    drivers: tuple[DriverTimeline, ...]

    @classmethod
    def from_laps(cls, rows: Iterable[LapRow]) -> "RaceTimeline":
        times: dict[str, dict[LapNumber, Milliseconds | None]] = {}
        for row in rows:
            times.setdefault(row.driver_id, {})[row.lap] = row.time_ms
        return cls(
            tuple(DriverTimeline(driver_id, crossings(laps)) for driver_id, laps in times.items())
        )

    def leader_crossing(self, lap: LapNumber) -> Milliseconds:
        return min(driver.crossings[lap - 1] for driver in self.drivers if driver.laps >= lap)


def crossings(laps: dict[LapNumber, Milliseconds | None]) -> tuple[Milliseconds, ...]:
    elapsed = 0
    result: list[Milliseconds] = []
    lap = LapNumber(1)
    while (time_ms := laps.get(lap)) is not None:
        elapsed += time_ms
        result.append(Milliseconds(elapsed))
        lap = LapNumber(lap + 1)
    return tuple(result)
