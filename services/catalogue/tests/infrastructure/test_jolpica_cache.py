from collections.abc import Mapping
from typing import Any

import pytest

from catalogue.infrastructure.jolpica import RetriesExhausted
from catalogue.infrastructure.jolpica_cache import CachedJolpica, cache_key
from catalogue.infrastructure.jolpica_pages import FetchJson, pages

from catalogue_tests.factories import EnvelopeFactory


class MemoryStore:
    def __init__(self) -> None:
        self.rows: dict[str, dict[str, Any]] = {}

    def get(self, url: str) -> dict[str, Any] | None:
        return self.rows.get(url)

    def put(self, url: str, body: dict[str, Any]) -> None:
        self.rows[url] = body


class CountingFetch:
    def __init__(self, fail_on_call: int | None = None) -> None:
        self.calls = 0
        self._fail_on_call = fail_on_call

    def __call__(self, path: str, params: Mapping[str, str | int] | None = None) -> dict[str, Any]:
        self.calls += 1
        if self.calls == self._fail_on_call:
            raise RetriesExhausted("network down")
        offset = int(params["offset"]) if params else 0
        return EnvelopeFactory.build(MRData__total="1000", MRData__offset=str(offset))


def test_cache_key_is_path_with_sorted_params() -> None:
    assert cache_key("/2025/1/laps.json", {"offset": 100, "limit": 100}) == (
        "/2025/1/laps.json?limit=100&offset=100"
    )
    assert cache_key("/2025/1/results.json", None) == "/2025/1/results.json"
    assert cache_key("/2025/1/results.json", {}) == "/2025/1/results.json"


def test_second_fetch_of_the_same_page_does_not_touch_the_network() -> None:
    fetch = CountingFetch()
    store = MemoryStore()
    cached: FetchJson = CachedJolpica(fetch, store)

    first = cached("/2025/1/laps.json", {"limit": 100, "offset": 0})
    second = cached("/2025/1/laps.json", {"limit": 100, "offset": 0})

    assert first == second
    assert fetch.calls == 1
    assert list(store.rows) == ["/2025/1/laps.json?limit=100&offset=0"]


def test_retry_after_a_failure_on_page_seven_fetches_only_the_missing_pages() -> None:
    store = MemoryStore()
    failing = CountingFetch(fail_on_call=7)
    with pytest.raises(RetriesExhausted):
        list(pages(CachedJolpica(failing, store), "/2025/1/laps.json"))

    healthy = CountingFetch()
    list(pages(CachedJolpica(healthy, store), "/2025/1/laps.json"))

    assert failing.calls == 7
    assert healthy.calls == 4
    assert len(store.rows) == 10
