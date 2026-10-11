import random
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

import httpx2

JsonObject = dict[str, Any]


class UpstreamUnavailable(Exception):
    pass


@dataclass(frozen=True, slots=True)
class Backoff:
    attempts: int = 4
    base_seconds: float = 0.5

    def delay(self, attempt: int, retry_after: float | None, jitter: float) -> float:
        exponential = self.base_seconds * 2.0**attempt
        return max(exponential, retry_after or 0.0) + jitter * self.base_seconds


class JolpicaClient:
    def __init__(
        self,
        http: httpx2.Client,
        backoff: Backoff | None = None,
        sleep: Callable[[float], None] = time.sleep,
        jitter: Callable[[], float] = random.random,
    ) -> None:
        self._http = http
        self._backoff = backoff or Backoff()
        self._sleep = sleep
        self._jitter = jitter

    def get_json(self, path: str, params: Mapping[str, str | int] | None = None) -> JsonObject:
        for attempt in range(self._backoff.attempts):
            response = self._http.get(path, params=params)
            if response.status_code == 200:
                data: JsonObject = response.json()
                return data
            if response.status_code != 429 and not response.is_server_error:
                raise UpstreamUnavailable(f"{response.status_code} from {response.request.url}")
            if attempt + 1 < self._backoff.attempts:
                self._sleep(self._backoff.delay(attempt, retry_after(response), self._jitter()))
        raise UpstreamUnavailable(f"gave up after {self._backoff.attempts} attempts on {path}")


def retry_after(response: httpx2.Response) -> float | None:
    header = response.headers.get("Retry-After")
    return float(header) if header else None
