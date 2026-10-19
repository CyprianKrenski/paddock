from collections.abc import Iterable, Mapping

from pydantic import SecretStr

from catalogue.entities.json_object import JsonObject
from catalogue.entities.race_snapshot import RaceInfo, RaceSnapshot
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
