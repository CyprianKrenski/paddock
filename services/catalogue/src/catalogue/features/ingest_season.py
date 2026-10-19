from typing import Protocol

from catalogue.entities.race_snapshot import RaceInfo
from catalogue.infrastructure.jolpica_pages import FetchJson, fetch_season_schedule


class ScheduleStore(Protocol):
    def save_schedule(self, races: tuple[RaceInfo, ...]) -> None: ...


class SeasonNotFound(Exception):
    pass


def ingest_season(fetch: FetchJson, store: ScheduleStore, season: int) -> int:
    schedule = fetch_season_schedule(fetch, season)
    if not schedule:
        raise SeasonNotFound(f"season {season} is unknown to the source")
    races = tuple(
        RaceInfo(
            season=race.season,
            round_number=race.round_number,
            name=race.name,
            circuit_id=race.circuit.circuit_id,
            circuit_name=race.circuit.circuit_name,
            date=race.date,
            total_laps=None,
        )
        for race in schedule
    )
    store.save_schedule(races)
    return len(races)
