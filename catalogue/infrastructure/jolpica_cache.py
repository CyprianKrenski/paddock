from collections.abc import Mapping
from typing import Protocol
from urllib.parse import urlencode

from catalogue.infrastructure.jolpica import JsonObject
from catalogue.infrastructure.jolpica_pages import FetchJson


class RawResponseStore(Protocol):
    def get(self, url: str) -> JsonObject | None: ...

    def put(self, url: str, body: JsonObject) -> None: ...


def cache_key(path: str, params: Mapping[str, str | int] | None) -> str:
    if not params:
        return path
    return f"{path}?{urlencode(sorted((key, str(value)) for key, value in params.items()))}"


class CachedJolpica:
    def __init__(self, fetch: FetchJson, store: RawResponseStore) -> None:
        self._fetch = fetch
        self._store = store

    def __call__(self, path: str, params: Mapping[str, str | int] | None = None) -> JsonObject:
        key = cache_key(path, params)
        cached = self._store.get(key)
        if cached is not None:
            return cached
        body = self._fetch(path, params)
        self._store.put(key, body)
        return body
