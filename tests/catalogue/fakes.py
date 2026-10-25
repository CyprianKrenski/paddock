from collections.abc import Iterable, Mapping
from datetime import date

from pydantic import SecretStr

from catalogue.entities.json_object import JsonObject
from catalogue.entities.race_snapshot import (
    LapRow,
    PitStopRow,
    RaceInfo,
    RaceSnapshot,
    RaceSummary,
    ResultRow,
    StandingRow,
)
from catalogue.entities.units import LapNumber, Milliseconds, Position, RoundNumber, Season
from catalogue.infrastructure.jolpica import RetriesExhausted
from catalogue.infrastructure.settings import Settings


class ScriptedFetch:
    def __init__(
        self,
        by_path: Mapping[str, JsonObject] | None = None,
        responses: Iterable[JsonObject] | None = None,
    ) -> None:
        self._by_path = dict(by_path or {})
        self._responses = iter(responses or ())
        self.calls: list[tuple[str, Mapping[str, str | int] | None]] = []

    def __call__(self, path: str, params: Mapping[str, str | int] | None = None) -> JsonObject:
        self.calls.append((path, params))
        if path in self._by_path:
            return self._by_path[path]
        return next(self._responses)


class CountingFetch:
    def __init__(self, page_total: str, fail_on_call: int | None = None) -> None:
        self.calls = 0
        self._page_total = page_total
        self._fail_on_call = fail_on_call

    def __call__(self, path: str, params: Mapping[str, str | int] | None = None) -> JsonObject:
        self.calls += 1
        if self.calls == self._fail_on_call:
            raise RetriesExhausted("network down")
        offset = int(params["offset"]) if params else 0
        return {"MRData": {"total": self._page_total, "limit": "100", "offset": str(offset)}}


class FailingFetch:
    def __call__(self, path: str, params: Mapping[str, str | int] | None = None) -> JsonObject:
        raise RetriesExhausted(f"gave up after 4 attempts on {path}")


class RecordingStore:
    def __init__(self) -> None:
        self.saved: list[RaceSnapshot] = []

    def save(self, snapshot: RaceSnapshot) -> None:
        self.saved.append(snapshot)


class RecordingScheduleStore:
    def __init__(self) -> None:
        self.saved: list[tuple[RaceInfo, ...]] = []

    def save_schedule(self, races: tuple[RaceInfo, ...]) -> None:
        self.saved.append(races)


class MemoryStore:
    def __init__(self) -> None:
        self.rows: dict[str, JsonObject] = {}

    def get(self, url: str) -> JsonObject | None:
        return self.rows.get(url)

    def put(self, url: str, body: JsonObject) -> None:
        self.rows[url] = body


def unreachable_settings() -> Settings:
    return Settings(
        postgres_user="x", postgres_password=SecretStr("x"), postgres_db="x", postgres_port=1
    )


NORRIS = (
    LapRow("norris", LapNumber(1), Position(1), Milliseconds(117099)),
    LapRow("norris", LapNumber(2), Position(1), Milliseconds(90553)),
)
PIASTRI = (
    LapRow("piastri", LapNumber(1), Position(2), Milliseconds(118000)),
    LapRow("piastri", LapNumber(2), Position(2), Milliseconds(90000)),
)
RESULTS = (
    ResultRow("norris", "NOR", "mclaren", Position(1), Position(1), LapNumber(2), "Finished"),
    ResultRow("piastri", "PIA", "mclaren", Position(2), Position(2), LapNumber(2), "Finished"),
    ResultRow("hadjar", "HAD", "rb", Position(20), Position(11), LapNumber(0), "Retired"),
)
PIT_STOPS = (PitStopRow("piastri", 1, LapNumber(2), Milliseconds(13341)),)
INGESTED = RaceSummary(
    Season(2025), RoundNumber(1), "Australian Grand Prix", "Albert Park", date(2025, 3, 16), True
)


class MemorySource:
    def __init__(
        self, laps: tuple[LapRow, ...] = NORRIS + PIASTRI, results: tuple[ResultRow, ...] = RESULTS
    ) -> None:
        self._laps = laps
        self._results = results

    def seasons(self) -> tuple[Season, ...]:
        return (Season(2025),)

    def races_of(self, season: Season) -> tuple[RaceSummary, ...]:
        return (INGESTED,)

    def race(self, season: Season, round_number: RoundNumber) -> RaceSummary | None:
        return INGESTED if round_number == 1 else None

    def results_of(self, season: Season, round_number: RoundNumber) -> tuple[ResultRow, ...]:
        return self._results

    def laps_of(self, season: Season, round_number: RoundNumber) -> tuple[LapRow, ...]:
        return self._laps

    def pit_stops_of(self, season: Season, round_number: RoundNumber) -> tuple[PitStopRow, ...]:
        return PIT_STOPS

    def standings_after(self, season: Season, round_number: RoundNumber) -> tuple[StandingRow, ...]:
        return ()
