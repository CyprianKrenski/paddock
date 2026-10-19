from fastapi import APIRouter

from catalogue.api.dependencies import DbSession, Fetch, RaceReaderDep, RaceStoreDep
from catalogue.entities.race_snapshot import LapRow, PitStopRow, ResultRow
from catalogue.features.ingest_race import IngestSummary, ingest_race
from catalogue.features.read_races import race_laps, race_pit_stops, race_results

router = APIRouter(prefix="/races")


@router.post("/{season}/{round_number}/ingest")
def ingest(
    season: int, round_number: int, fetch: Fetch, store: RaceStoreDep, session: DbSession
) -> IngestSummary:
    summary = ingest_race(fetch, store, season=season, round_number=round_number)
    session.commit()
    return summary


@router.get("/{season}/{round_number}/results")
def results(season: int, round_number: int, reader: RaceReaderDep) -> list[ResultRow]:
    return list(race_results(reader, season, round_number))


@router.get("/{season}/{round_number}/laps")
def laps(season: int, round_number: int, reader: RaceReaderDep) -> list[LapRow]:
    return list(race_laps(reader, season, round_number))


@router.get("/{season}/{round_number}/pit-stops")
def pit_stops(season: int, round_number: int, reader: RaceReaderDep) -> list[PitStopRow]:
    return list(race_pit_stops(reader, season, round_number))
