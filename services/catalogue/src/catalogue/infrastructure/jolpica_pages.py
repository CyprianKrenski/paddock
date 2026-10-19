from collections.abc import Iterator, Mapping
from datetime import date
from typing import Protocol

from pydantic import BaseModel, Field

from catalogue.entities.json_object import JsonObject

MAX_PAGE_SIZE = 100


class FetchJson(Protocol):
    def __call__(self, path: str, params: Mapping[str, str | int] | None = None) -> JsonObject: ...


class PageInfo(BaseModel):
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


class Envelope(BaseModel):
    page: PageInfo = Field(alias="MRData")


def pages(fetch: FetchJson, path: str) -> Iterator[JsonObject]:
    first = fetch(path, {"limit": MAX_PAGE_SIZE, "offset": 0})
    yield first
    page = Envelope.model_validate(first).page
    for offset in range(page.limit, page.total, page.limit):
        yield fetch(path, {"limit": MAX_PAGE_SIZE, "offset": offset})


class RaceTable(BaseModel):
    races: list[JsonObject] = Field(alias="Races")


class RaceTablePage(BaseModel):
    table: RaceTable = Field(alias="RaceTable")


class RaceEnvelope(BaseModel):
    data: RaceTablePage = Field(alias="MRData")


def races_in[R: BaseModel](payload: JsonObject, race: type[R]) -> list[R]:
    table = RaceEnvelope.model_validate(payload).data.table
    return [race.model_validate(item) for item in table.races]


class Timing(BaseModel):
    driver_id: str = Field(alias="driverId")
    position: int
    time: str | None = None


class Lap(BaseModel):
    number: int
    timings: list[Timing] = Field(alias="Timings")


class LapsRace(BaseModel):
    laps: list[Lap] = Field(alias="Laps")


class LapTiming(BaseModel):
    lap: int
    driver_id: str
    position: int
    time: str | None


def fetch_lap_timings(fetch: FetchJson, season: int, round_number: int) -> Iterator[LapTiming]:
    for payload in pages(fetch, f"/{season}/{round_number}/laps.json"):
        for race in races_in(payload, LapsRace):
            for lap in race.laps:
                for timing in lap.timings:
                    yield LapTiming(
                        lap=lap.number,
                        driver_id=timing.driver_id,
                        position=timing.position,
                        time=timing.time,
                    )


class DriverRef(BaseModel):
    driver_id: str = Field(alias="driverId")
    code: str | None = None
    given_name: str = Field(alias="givenName")
    family_name: str = Field(alias="familyName")


class ResultEntry(BaseModel):
    position: int | None = None
    grid: int
    laps: int
    status: str
    driver: DriverRef = Field(alias="Driver")


class Circuit(BaseModel):
    circuit_id: str = Field(alias="circuitId")
    circuit_name: str = Field(alias="circuitName")


class ResultsRace(BaseModel):
    season: int
    round_number: int = Field(alias="round")
    name: str = Field(alias="raceName")
    circuit: Circuit = Field(alias="Circuit")
    date: date
    results: list[ResultEntry] = Field(alias="Results")


def fetch_race_results(fetch: FetchJson, season: int, round_number: int) -> ResultsRace | None:
    payload = fetch(f"/{season}/{round_number}/results.json", {"limit": MAX_PAGE_SIZE, "offset": 0})
    races = races_in(payload, ResultsRace)
    return races[0] if races else None


class PitStopEntry(BaseModel):
    driver_id: str = Field(alias="driverId")
    lap: int
    stop: int
    duration: str | None = None


class PitStopsRace(BaseModel):
    pit_stops: list[PitStopEntry] = Field(alias="PitStops")


def fetch_pit_stops(fetch: FetchJson, season: int, round_number: int) -> Iterator[PitStopEntry]:
    for payload in pages(fetch, f"/{season}/{round_number}/pitstops.json"):
        for race in races_in(payload, PitStopsRace):
            yield from race.pit_stops


class ScheduleRace(BaseModel):
    season: int
    round_number: int = Field(alias="round")
    name: str = Field(alias="raceName")
    circuit: Circuit = Field(alias="Circuit")
    date: date


def fetch_season_schedule(fetch: FetchJson, season: int) -> list[ScheduleRace]:
    found: list[ScheduleRace] = []
    for payload in pages(fetch, f"/{season}.json"):
        found.extend(races_in(payload, ScheduleRace))
    return found
