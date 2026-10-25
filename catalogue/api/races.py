from fastapi import APIRouter

from catalogue.api.dependencies import DbSession, Fetch, RaceReaderDep, RaceStoreDep
from catalogue.entities.race_snapshot import LapRow, PitStopRow, ResultRow
from catalogue.entities.units import RoundNumber, Season
from catalogue.features.ingest_race import IngestSummary, ingest_race
from catalogue.features.read_races import ingested_race, race_laps, race_pit_stops, race_results
from catalogue.features.replay import Replay, build_replay
from catalogue.features.trace import Trace, build_trace

router = APIRouter(prefix="/races")


@router.post("/{season}/{round_number}/ingest")
def ingest(
    season: Season, round_number: RoundNumber, fetch: Fetch, store: RaceStoreDep, session: DbSession
) -> IngestSummary:
    summary = ingest_race(fetch, store, season=season, round_number=round_number)
    session.commit()
    return summary


@router.get("/{season}/{round_number}/results")
def results(season: Season, round_number: RoundNumber, reader: RaceReaderDep) -> list[ResultRow]:
    return list(race_results(reader, season, round_number))


@router.get("/{season}/{round_number}/laps")
def laps(season: Season, round_number: RoundNumber, reader: RaceReaderDep) -> list[LapRow]:
    return list(race_laps(reader, season, round_number))


@router.get("/{season}/{round_number}/pit-stops")
def pit_stops(season: Season, round_number: RoundNumber, reader: RaceReaderDep) -> list[PitStopRow]:
    return list(race_pit_stops(reader, season, round_number))


@router.get("/{season}/{round_number}/trace")
def trace(season: Season, round_number: RoundNumber, reader: RaceReaderDep) -> Trace:
    ingested_race(reader, season, round_number)
    return build_trace(reader, season, round_number)


@router.get("/{season}/{round_number}/replay")
def replay(season: Season, round_number: RoundNumber, reader: RaceReaderDep) -> Replay:
    ingested_race(reader, season, round_number)
    return build_replay(reader, season, round_number)
