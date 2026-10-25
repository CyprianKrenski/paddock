from dataclasses import asdict
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from catalogue.entities.models import Driver, DriverStanding, Lap, PitStop, Race, Result
from catalogue.entities.race_snapshot import RaceInfo, RaceSnapshot, ResultRow


class SqlRaceStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, snapshot: RaceSnapshot) -> None:
        race_id = self._upsert_race(snapshot)
        self._upsert(Driver, [asdict(driver) for driver in snapshot.drivers], ["id"])
        self._upsert(
            Result,
            [{"race_id": race_id, **result_columns(row)} for row in snapshot.results],
            ["race_id", "driver_id"],
        )
        self._upsert(
            Lap,
            [{"race_id": race_id, **asdict(row)} for row in snapshot.laps],
            ["race_id", "driver_id", "lap"],
        )
        self._upsert(
            PitStop,
            [{"race_id": race_id, **asdict(row)} for row in snapshot.pit_stops],
            ["race_id", "driver_id", "stop"],
        )
        before = snapshot.race.round_number - 1
        self._upsert(
            DriverStanding,
            [
                {"season": snapshot.race.season, "round": before, **asdict(row)}
                for row in snapshot.standings_before
            ],
            ["season", "round", "driver_id"],
        )

    def save_schedule(self, races: tuple[RaceInfo, ...]) -> None:
        rows = [asdict(race) for race in races]
        inserted = insert(Race).values(rows)
        refreshed = ("name", "circuit_id", "circuit_name", "date")
        self._session.execute(
            inserted.on_conflict_do_update(
                index_elements=["season", "round"],
                set_={column: inserted.excluded[column] for column in refreshed},
            )
        )

    def _upsert_race(self, snapshot: RaceSnapshot) -> int:
        inserted = insert(Race).values(asdict(snapshot.race))
        refreshed = ("name", "circuit_id", "circuit_name", "date", "total_laps")
        upsert = inserted.on_conflict_do_update(
            index_elements=["season", "round"],
            set_={column: inserted.excluded[column] for column in refreshed},
        )
        race_id: int = self._session.execute(upsert.returning(Race.id)).scalar_one()
        return race_id

    def _upsert(self, model: type[Any], rows: list[dict[str, Any]], key: list[str]) -> None:
        if not rows:
            return
        statement = insert(model).values(rows)
        updates = {column: statement.excluded[column] for column in rows[0] if column not in key}
        self._session.execute(statement.on_conflict_do_update(index_elements=key, set_=updates))


def result_columns(row: ResultRow) -> dict[str, Any]:
    columns = asdict(row)
    del columns["code"]
    return columns
