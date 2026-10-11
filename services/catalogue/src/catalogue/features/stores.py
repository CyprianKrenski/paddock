from typing import Any, Protocol

JsonObject = dict[str, Any]


class RawResponseStore(Protocol):
    def get(self, url: str) -> JsonObject | None: ...

    def put(self, url: str, body: JsonObject) -> None: ...
