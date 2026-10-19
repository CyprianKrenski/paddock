import pytest

from catalogue.infrastructure.jolpica import RetriesExhausted
from catalogue.infrastructure.jolpica_cache import CachedJolpica, cache_key
from catalogue.infrastructure.jolpica_pages import FetchJson, pages

from catalogue_tests.fakes import CountingFetch, MemoryStore


def test_cache_key_is_path_with_sorted_params() -> None:
    assert cache_key("/2025/1/laps.json", {"offset": 100, "limit": 100}) == (
        "/2025/1/laps.json?limit=100&offset=100"
    )
    assert cache_key("/2025/1/results.json", None) == "/2025/1/results.json"
    assert cache_key("/2025/1/results.json", {}) == "/2025/1/results.json"


def test_second_fetch_of_the_same_page_does_not_touch_the_network() -> None:
    fetch = CountingFetch(page_total="1000")
    store = MemoryStore()
    cached: FetchJson = CachedJolpica(fetch, store)

    first = cached("/2025/1/laps.json", {"limit": 100, "offset": 0})
    second = cached("/2025/1/laps.json", {"limit": 100, "offset": 0})

    assert first == second
    assert fetch.calls == 1
    assert list(store.rows) == ["/2025/1/laps.json?limit=100&offset=0"]


def test_retry_after_a_failure_on_page_seven_fetches_only_the_missing_pages() -> None:
    store = MemoryStore()
    failing = CountingFetch(page_total="1000", fail_on_call=7)
    with pytest.raises(RetriesExhausted):
        list(pages(CachedJolpica(failing, store), "/2025/1/laps.json"))

    healthy = CountingFetch(page_total="1000")
    list(pages(CachedJolpica(healthy, store), "/2025/1/laps.json"))

    assert failing.calls == 7
    assert healthy.calls == 4
    assert len(store.rows) == 10
