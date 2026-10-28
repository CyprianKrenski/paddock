from dataclasses import replace
from datetime import date

import pytest
from sqlalchemy.orm import Session, sessionmaker

from catalogue.entities.race_snapshot import (
    DriverInfo,
    LapRow,
    PitStopRow,
    RaceInfo,
    RaceSnapshot,
    RaceSummary,
    ResultRow,
    StandingRow,
)
from catalogue.entities.units import LapNumber, Milliseconds, Position, RoundNumber, Season
from catalogue.infrastructure.race_reader import SqlRaceReader
from catalogue.infrastructure.race_store import SqlRaceStore

pytestmark = pytest.mark.integration

SCHEDULE = (
    RaceInfo(
        Season(1900),
        RoundNumber(1),
        "First Grand Prix",
        "nowhere",
        "Nowhere Circuit",
        date(1900, 1, 1),
        None,
    ),
    RaceInfo(
        Season(1900),
        RoundNumber(2),
        "Second Grand Prix",
        "elsewhere",
        "Elsewhere Circuit",
        date(1900, 2, 1),
        None,
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
                    Season(1900),
                    RoundNumber(1),
                    "First Grand Prix",
                    "nowhere",
                    "Nowhere Circuit",
                    date(1900, 1, 1),
                    LapNumber(2),
                ),
                drivers=(DriverInfo("norris", "NOR", "Lando", "Norris"),),
                results=(
                    ResultRow(
                        "norris", None, None, Position(1), Position(1), LapNumber(2), "Finished"
                    ),
                ),
                laps=(
                    LapRow("norris", LapNumber(1), Position(1), Milliseconds(100000)),
                    LapRow("norris", LapNumber(2), Position(1), Milliseconds(99000)),
                ),
                pit_stops=(),
            )
        )
        store.save_schedule(SCHEDULE)

        assert Season(1900) in reader.seasons()
        assert reader.races_of(Season(1900)) == (
            RaceSummary(
                Season(1900),
                RoundNumber(1),
                "First Grand Prix",
                "Nowhere Circuit",
                date(1900, 1, 1),
                ingested=True,
            ),
            RaceSummary(
                Season(1900),
                RoundNumber(2),
                "Second Grand Prix",
                "Elsewhere Circuit",
                date(1900, 2, 1),
                ingested=False,
            ),
        )
        assert reader.laps_of(Season(1900), RoundNumber(1)) == (
            LapRow("norris", LapNumber(1), Position(1), Milliseconds(100000)),
            LapRow("norris", LapNumber(2), Position(1), Milliseconds(99000)),
        )
        assert reader.laps_of(Season(1900), RoundNumber(2)) == ()


def test_standings_before_a_round_round_trip(db_sessions: sessionmaker[Session]) -> None:
    with db_sessions() as session:
        store = SqlRaceStore(session)
        reader = SqlRaceReader(session)
        store.save(
            RaceSnapshot(
                race=RaceInfo(
                    Season(1900),
                    RoundNumber(2),
                    "Second Grand Prix",
                    "nowhere",
                    "Nowhere Circuit",
                    date(1900, 2, 1),
                    LapNumber(1),
                ),
                drivers=(DriverInfo("norris", "NOR", "Lando", "Norris"),),
                results=(
                    ResultRow(
                        "norris", None, None, Position(1), Position(1), LapNumber(1), "Finished"
                    ),
                ),
                laps=(LapRow("norris", LapNumber(1), Position(1), Milliseconds(100000)),),
                pit_stops=(),
                standings_before=(
                    StandingRow("norris", Position(1), 25.0, 1),
                    StandingRow("piastri", Position(2), 18.0, 0),
                ),
            )
        )

        assert reader.standings_after(Season(1900), RoundNumber(1)) == (
            StandingRow("norris", Position(1), 25.0, 1),
            StandingRow("piastri", Position(2), 18.0, 0),
        )
        assert reader.standings_after(Season(1900), RoundNumber(2)) == ()


def test_a_saved_race_reads_back_results_laps_and_pit_stops(
    db_sessions: sessionmaker[Session],
) -> None:
    with db_sessions() as session:
        store = SqlRaceStore(session)
        reader = SqlRaceReader(session)
        store.save(
            RaceSnapshot(
                race=replace(SCHEDULE[0], total_laps=LapNumber(2)),
                drivers=(
                    DriverInfo("hadjar", "HAD", "Isack", "Hadjar"),
                    DriverInfo("norris", "NOR", "Lando", "Norris"),
                ),
                results=(
                    ResultRow("hadjar", None, "rb", None, Position(11), LapNumber(0), "Retired"),
                    ResultRow(
                        "norris",
                        None,
                        "mclaren",
                        Position(1),
                        Position(2),
                        LapNumber(2),
                        "Finished",
                    ),
                ),
                laps=(
                    LapRow("norris", LapNumber(2), Position(1), None),
                    LapRow("norris", LapNumber(1), Position(1), Milliseconds(100000)),
                ),
                pit_stops=(
                    PitStopRow("norris", 2, LapNumber(2), None),
                    PitStopRow("norris", 1, LapNumber(1), Milliseconds(22000)),
                ),
            )
        )

        assert reader.race(Season(1900), RoundNumber(1)) == RaceSummary(
            Season(1900),
            RoundNumber(1),
            "First Grand Prix",
            "Nowhere Circuit",
            date(1900, 1, 1),
            ingested=True,
        )
        assert reader.results_of(Season(1900), RoundNumber(1)) == (
            ResultRow(
                "norris", "NOR", "mclaren", Position(1), Position(2), LapNumber(2), "Finished"
            ),
            ResultRow("hadjar", "HAD", "rb", None, Position(11), LapNumber(0), "Retired"),
        )
        assert reader.laps_of(Season(1900), RoundNumber(1)) == (
            LapRow("norris", LapNumber(1), Position(1), Milliseconds(100000)),
            LapRow("norris", LapNumber(2), Position(1), None),
        )
        assert reader.pit_stops_of(Season(1900), RoundNumber(1)) == (
            PitStopRow("norris", 1, LapNumber(1), Milliseconds(22000)),
            PitStopRow("norris", 2, LapNumber(2), None),
        )
        assert reader.race(Season(1900), RoundNumber(9)) is None
        assert reader.results_of(Season(1900), RoundNumber(9)) == ()
        assert reader.laps_of(Season(1900), RoundNumber(9)) == ()
        assert reader.pit_stops_of(Season(1900), RoundNumber(9)) == ()
