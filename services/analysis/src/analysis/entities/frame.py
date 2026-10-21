from collections.abc import Mapping
from dataclasses import dataclass

from analysis.entities.rows import ResultRow
from analysis.entities.timeline import DriverTimeline, RaceTimeline
from analysis.entities.units import Distance, DriverStatus, LapNumber, Milliseconds, Position


@dataclass(frozen=True, slots=True)
class DriverState:
    driver_id: str
    position: Position
    laps_completed: LapNumber
    distance: Distance
    gap_ms: Milliseconds | None
    status: DriverStatus


@dataclass(frozen=True, slots=True)
class Progress:
    driver: DriverTimeline
    distance: Distance
    laps_completed: LapNumber
    lap_start: Milliseconds
    lap_ms: Milliseconds
    status: DriverStatus
    grid: Position

    @property
    def order(self) -> tuple[bool, float, Milliseconds, bool, Position]:
        return (
            self.status is DriverStatus.OUT,
            -self.distance,
            self.lap_start,
            self.grid == 0,
            self.grid,
        )

    def gap_to(self, leader_distance: Distance) -> Milliseconds | None:
        if self.status is not DriverStatus.RUNNING:
            return None
        return Milliseconds(round((leader_distance - self.distance) * self.lap_ms))


def replay_frame(
    timeline: RaceTimeline, results: Mapping[str, ResultRow], at_ms: Milliseconds
) -> tuple[DriverState, ...]:
    progress = sorted(
        (driver_progress(driver, results[driver.driver_id], at_ms) for driver in timeline.drivers),
        key=lambda item: item.order,
    )
    leader_distance = progress[0].distance if progress else Distance(0.0)
    return tuple(
        DriverState(
            driver_id=item.driver.driver_id,
            position=Position(position),
            laps_completed=item.laps_completed,
            distance=item.distance,
            gap_ms=item.gap_to(leader_distance),
            status=item.status,
        )
        for position, item in enumerate(progress, start=1)
    )


def driver_progress(driver: DriverTimeline, result: ResultRow, at_ms: Milliseconds) -> Progress:
    if at_ms >= driver.last_crossing:
        status = DriverStatus.FINISHED if result.classified else DriverStatus.OUT
        return Progress(
            driver,
            Distance(float(driver.laps)),
            driver.laps,
            driver.last_crossing,
            Milliseconds(0),
            status,
            result.grid,
        )
    completed = LapNumber(sum(1 for crossing in driver.crossings if crossing <= at_ms))
    lap_start = driver.crossings[completed - 1] if completed else Milliseconds(0)
    lap_ms = Milliseconds(driver.crossings[completed] - lap_start)
    fraction = (at_ms - lap_start) / lap_ms
    return Progress(
        driver,
        Distance(completed + fraction),
        completed,
        lap_start,
        lap_ms,
        DriverStatus.RUNNING,
        result.grid,
    )
