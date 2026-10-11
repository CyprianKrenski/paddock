from collections.abc import Iterator, Mapping
from typing import Protocol

from pydantic import BaseModel, Field

from catalogue.infrastructure.jolpica import JsonObject

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


class Timing(BaseModel):
    driver_id: str = Field(alias="driverId")
    position: int
    time: str | None = None


class Lap(BaseModel):
    number: int
    timings: list[Timing] = Field(alias="Timings")


class LapsRace(BaseModel):
    laps: list[Lap] = Field(alias="Laps")


class LapsTable(BaseModel):
    races: list[LapsRace] = Field(alias="Races")


class LapsPage(BaseModel):
    table: LapsTable = Field(alias="RaceTable")


class LapsEnvelope(BaseModel):
    data: LapsPage = Field(alias="MRData")


class LapTiming(BaseModel):
    lap: int
    driver_id: str
    position: int
    time: str | None


def lap_timings(fetch: FetchJson, season: int, round_number: int) -> Iterator[LapTiming]:
    for payload in pages(fetch, f"/{season}/{round_number}/laps.json"):
        for race in LapsEnvelope.model_validate(payload).data.table.races:
            for lap in race.laps:
                for timing in lap.timings:
                    yield LapTiming(
                        lap=lap.number,
                        driver_id=timing.driver_id,
                        position=timing.position,
                        time=timing.time,
                    )
