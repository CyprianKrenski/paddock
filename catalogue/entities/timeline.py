from collections.abc import Iterable
from dataclasses import dataclass

from catalogue.entities.race_snapshot import LapRow
from catalogue.entities.units import LapNumber, Milliseconds, Position


@dataclass(frozen=True, slots=True)
class DriverTimeline:
    driver_id: str
    crossings: tuple[Milliseconds, ...]
    positions: tuple[Position, ...]

    @property
    def laps(self) -> LapNumber:
        return LapNumber(len(self.crossings))

    @property
    def last_crossing(self) -> Milliseconds:
        return self.crossings[-1] if self.crossings else Milliseconds(0)

    def lap_time(self, lap: LapNumber) -> Milliseconds:
        previous = self.crossings[lap - 2] if lap > 1 else Milliseconds(0)
        return Milliseconds(self.crossings[lap - 1] - previous)


@dataclass(frozen=True, slots=True)
class RaceTimeline:
    drivers: tuple[DriverTimeline, ...]

    @classmethod
    def from_laps(cls, rows: Iterable[LapRow], driver_ids: Iterable[str] = ()) -> "RaceTimeline":
        times: dict[str, dict[LapNumber, LapRow]] = {driver_id: {} for driver_id in driver_ids}
        for row in rows:
            times.setdefault(row.driver_id, {})[row.lap] = row
        return cls(tuple(driver_timeline(driver_id, laps) for driver_id, laps in times.items()))

    @property
    def total_laps(self) -> LapNumber:
        return max((driver.laps for driver in self.drivers), default=LapNumber(0))

    def leader_crossing(self, lap: LapNumber) -> Milliseconds:
        return min(driver.crossings[lap - 1] for driver in self.drivers if driver.laps >= lap)

    def leader_crossings(self) -> tuple[Milliseconds, ...]:
        return tuple(self.leader_crossing(LapNumber(lap)) for lap in range(1, self.total_laps + 1))


def driver_timeline(driver_id: str, laps: dict[LapNumber, LapRow]) -> DriverTimeline:
    elapsed = 0
    crossings: list[Milliseconds] = []
    positions: list[Position] = []
    lap = LapNumber(1)
    while (row := laps.get(lap)) is not None and row.time_ms is not None:
        elapsed += row.time_ms
        crossings.append(Milliseconds(elapsed))
        positions.append(row.position)
        lap = LapNumber(lap + 1)
    return DriverTimeline(driver_id, tuple(crossings), tuple(positions))
