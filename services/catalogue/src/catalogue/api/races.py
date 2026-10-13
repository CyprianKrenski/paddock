from collections.abc import Callable

from fastapi import APIRouter, HTTPException

from catalogue.api.dependencies import RaceReaderDep
from catalogue.entities.race_snapshot import LapRow, PitStopRow, ResultRow
from catalogue.features.read_races import (
    RaceNotIngested,
    RaceReader,
    race_laps,
    race_pit_stops,
    race_results,
)

router = APIRouter(prefix="/races")


def read[T](
    query: Callable[[RaceReader, int, int], tuple[T, ...]],
    reader: RaceReader,
    season: int,
    round_number: int,
) -> list[T]:
    try:
        return list(query(reader, season, round_number))
    except RaceNotIngested as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{season}/{round_number}/results")
def results(season: int, round_number: int, reader: RaceReaderDep) -> list[ResultRow]:
    return read(race_results, reader, season, round_number)


@router.get("/{season}/{round_number}/laps")
def laps(season: int, round_number: int, reader: RaceReaderDep) -> list[LapRow]:
    return read(race_laps, reader, season, round_number)


@router.get("/{season}/{round_number}/pit-stops")
def pit_stops(season: int, round_number: int, reader: RaceReaderDep) -> list[PitStopRow]:
    return read(race_pit_stops, reader, season, round_number)
