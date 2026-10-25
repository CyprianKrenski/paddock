from fastapi import APIRouter

from catalogue.api.dependencies import DbSession, Fetch, RaceReaderDep, RaceStoreDep
from catalogue.entities.units import RoundNumber, Season
from catalogue.features.ingest_race import IngestSummary, ingest_race
from catalogue.features.read_races import ingested_race
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


@router.get("/{season}/{round_number}/trace")
def trace(season: Season, round_number: RoundNumber, reader: RaceReaderDep) -> Trace:
    ingested_race(reader, season, round_number)
    return build_trace(reader, season, round_number)


@router.get("/{season}/{round_number}/replay")
def replay(season: Season, round_number: RoundNumber, reader: RaceReaderDep) -> Replay:
    ingested_race(reader, season, round_number)
    return build_replay(reader, season, round_number)
