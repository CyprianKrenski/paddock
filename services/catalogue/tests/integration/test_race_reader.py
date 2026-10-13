from datetime import date

import pytest
from sqlalchemy.orm import Session, sessionmaker

from catalogue.entities.lap_time import LapTimeMs
from catalogue.entities.race_snapshot import (
    DriverInfo,
    LapRow,
    RaceInfo,
    RaceSnapshot,
    RaceSummary,
    ResultRow,
)
from catalogue.infrastructure.race_reader import SqlRaceReader
from catalogue.infrastructure.race_store import SqlRaceStore

pytestmark = pytest.mark.integration

SCHEDULE = (
    RaceInfo(1900, 1, "First Grand Prix", "nowhere", "Nowhere Circuit", date(1900, 1, 1), None),
    RaceInfo(
        1900, 2, "Second Grand Prix", "elsewhere", "Elsewhere Circuit", date(1900, 2, 1), None
    ),
)


def test_schedule_then_ingest_marks_only_the_ingested_round(
    db_sessions: sessionmaker[Session],
) -> None:
    with db_sessions() as session:
        store = SqlRaceStore(session)
        reader = SqlRaceReader(session)
        store.save_schedule(SCHEDULE)
        store.save(
            RaceSnapshot(
                race=RaceInfo(
                    1900, 1, "First Grand Prix", "nowhere", "Nowhere Circuit", date(1900, 1, 1), 2
                ),
                drivers=(DriverInfo("norris", "NOR", "Lando", "Norris"),),
                results=(ResultRow("norris", 1, 1, 2, "Finished"),),
                laps=(
                    LapRow("norris", 1, 1, LapTimeMs(100000)),
                    LapRow("norris", 2, 1, LapTimeMs(99000)),
                ),
                pit_stops=(),
            )
        )
        store.save_schedule(SCHEDULE)

        assert 1900 in reader.seasons()
        assert reader.races_of(1900) == (
            RaceSummary(
                1900, 1, "First Grand Prix", "Nowhere Circuit", date(1900, 1, 1), ingested=True
            ),
            RaceSummary(
                1900, 2, "Second Grand Prix", "Elsewhere Circuit", date(1900, 2, 1), ingested=False
            ),
        )
        assert reader.laps_of(1900, 1) == (
            LapRow("norris", 1, 1, LapTimeMs(100000)),
            LapRow("norris", 2, 1, LapTimeMs(99000)),
        )
        assert reader.laps_of(1900, 2) == ()
