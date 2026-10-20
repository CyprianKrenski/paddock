from sqlalchemy import select
from sqlalchemy.orm import Session

from catalogue.entities.lap_time import LapTimeMs
from catalogue.entities.models import Lap, PitStop, Race, Result
from catalogue.entities.race_snapshot import LapRow, PitStopRow, RaceSummary, ResultRow
from catalogue.entities.units import LapNumber, Position, RoundNumber, Season


class SqlRaceReader:
    def __init__(self, session: Session) -> None:
        self._session = session

    def seasons(self) -> tuple[Season, ...]:
        rows = self._session.scalars(select(Race.season).distinct().order_by(Race.season))
        return tuple(Season(row) for row in rows)

    def races_of(self, season: Season) -> tuple[RaceSummary, ...]:
        rows = self._session.scalars(
            select(Race).where(Race.season == season).order_by(Race.round_number)
        )
        return tuple(summary(race) for race in rows)

    def race(self, season: Season, round_number: RoundNumber) -> RaceSummary | None:
        race = self._race(season, round_number)
        return summary(race) if race else None

    def results_of(self, season: Season, round_number: RoundNumber) -> tuple[ResultRow, ...]:
        race = self._race(season, round_number)
        if race is None:
            return ()
        rows = self._session.scalars(
            select(Result).where(Result.race_id == race.id).order_by(Result.position)
        )
        return tuple(
            ResultRow(
                row.driver_id,
                Position(row.position) if row.position is not None else None,
                Position(row.grid),
                LapNumber(row.laps),
                row.status,
            )
            for row in rows
        )

    def laps_of(self, season: Season, round_number: RoundNumber) -> tuple[LapRow, ...]:
        race = self._race(season, round_number)
        if race is None:
            return ()
        rows = self._session.scalars(
            select(Lap).where(Lap.race_id == race.id).order_by(Lap.lap, Lap.position)
        )
        return tuple(
            LapRow(row.driver_id, LapNumber(row.lap), Position(row.position), lap_time(row.time_ms))
            for row in rows
        )

    def pit_stops_of(self, season: Season, round_number: RoundNumber) -> tuple[PitStopRow, ...]:
        race = self._race(season, round_number)
        if race is None:
            return ()
        rows = self._session.scalars(
            select(PitStop).where(PitStop.race_id == race.id).order_by(PitStop.lap, PitStop.stop)
        )
        return tuple(
            PitStopRow(row.driver_id, row.stop, LapNumber(row.lap), lap_time(row.duration_ms))
            for row in rows
        )

    def _race(self, season: Season, round_number: RoundNumber) -> Race | None:
        return self._session.scalar(
            select(Race).where(Race.season == season, Race.round_number == round_number)
        )


def summary(race: Race) -> RaceSummary:
    return RaceSummary(
        season=Season(race.season),
        round_number=RoundNumber(race.round_number),
        name=race.name,
        circuit_name=race.circuit_name,
        date=race.date,
        ingested=race.total_laps is not None,
    )


def lap_time(value: int | None) -> LapTimeMs | None:
    return LapTimeMs(value) if value is not None else None
