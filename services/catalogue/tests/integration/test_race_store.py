from datetime import date

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from catalogue.entities.lap_time import LapTimeMs
from catalogue.entities.models import Lap, Race
from catalogue.entities.race_snapshot import (
    DriverInfo,
    LapRow,
    PitStopRow,
    RaceInfo,
    RaceSnapshot,
    ResultRow,
)
from catalogue.entities.units import LapNumber, Position, RoundNumber, Season
from catalogue.infrastructure.race_store import SqlRaceStore

pytestmark = pytest.mark.integration


def snapshot(lap_time: int) -> RaceSnapshot:
    return RaceSnapshot(
        race=RaceInfo(
            Season(1900),
            RoundNumber(1),
            "Synthetic Grand Prix",
            "nowhere",
            "Nowhere Circuit",
            date(1900, 1, 1),
            LapNumber(57),
        ),
        drivers=(
            DriverInfo("norris", "NOR", "Lando", "Norris"),
            DriverInfo("hadjar", "HAD", "Isack", "Hadjar"),
        ),
        results=(
            ResultRow("norris", None, None, Position(1), Position(1), LapNumber(57), "Finished"),
            ResultRow("hadjar", None, None, Position(20), Position(11), LapNumber(0), "Retired"),
        ),
        laps=(LapRow("norris", LapNumber(1), Position(1), LapTimeMs(lap_time)),),
        pit_stops=(PitStopRow("norris", 1, LapNumber(2), LapTimeMs(13341)),),
    )


def test_saving_twice_is_idempotent_and_updates_values(db_sessions: sessionmaker[Session]) -> None:
    with db_sessions() as session:
        store = SqlRaceStore(session)

        synthetic = select(Race.id).where(Race.season == 1900, Race.round_number == 1)

        store.save(snapshot(lap_time=117099))
        first_id = session.scalar(synthetic)
        store.save(snapshot(lap_time=117000))

        assert session.scalar(synthetic) == first_id
        assert (
            session.scalar(select(func.count()).select_from(Race).where(Race.season == 1900)) == 1
        )
        assert (
            session.scalar(select(func.count()).select_from(Lap).where(Lap.race_id == first_id))
            == 1
        )
        assert session.scalar(select(Lap.time_ms).where(Lap.race_id == first_id)) == 117000
