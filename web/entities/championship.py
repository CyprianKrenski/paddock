from collections.abc import Sequence
from dataclasses import dataclass

from web.entities.points import fastest_lap_bonus, points_for
from web.entities.standings import StandingRow, standings_at
from web.entities.teams import driver_label
from web.entities.units import LapNumber
from web.entities.views import StandingBefore, Trace

OUTSIDER_COLOR = "#555"


@dataclass(frozen=True, slots=True)
class ChampionshipRow:
    rank: int
    code: str
    team: str
    color: str
    dashed: bool
    points: float
    gained: int
    delta: int | None


@dataclass(frozen=True, slots=True)
class Projection:
    driver_id: str
    row: StandingRow | None
    before: StandingBefore | None
    gained: int

    @property
    def points(self) -> float:
        return (self.before.points if self.before else 0.0) + self.gained

    @property
    def wins(self) -> int:
        won = self.row is not None and self.row.rank == 1 and self.gained > 0
        return (self.before.wins if self.before else 0) + int(won)

    @property
    def order(self) -> tuple[float, int, int]:
        return (-self.points, -self.wins, self.before.position if self.before else 999)


def championship_at(
    trace: Trace, before: Sequence[StandingBefore], lap: LapNumber
) -> tuple[ChampionshipRow, ...]:
    rows = standings_at(trace, lap).rows
    previous = {entry.driver_id: entry for entry in before}
    racing = {row.driver_id for row in rows}
    projections = [
        Projection(row.driver_id, row, previous.get(row.driver_id), race_points(trace, row, lap))
        for row in rows
    ] + [
        Projection(driver_id, None, entry, 0)
        for driver_id, entry in previous.items()
        if driver_id not in racing
    ]
    return tuple(
        ChampionshipRow(
            rank,
            item.row.code if item.row else driver_label(None, item.driver_id),
            item.row.team if item.row else "",
            item.row.color if item.row else OUTSIDER_COLOR,
            item.row.dashed if item.row else False,
            item.points,
            item.gained,
            item.before.position - rank if item.before else None,
        )
        for rank, item in enumerate(sorted(projections, key=lambda item: item.order), start=1)
    )


def race_points(trace: Trace, row: StandingRow, lap: LapNumber) -> int:
    if lap == 0 or row.out:
        return 0
    bonus = fastest_lap_bonus(trace.season, row.rank) if row.fastest else 0
    return points_for(trace.season, row.rank) + bonus
