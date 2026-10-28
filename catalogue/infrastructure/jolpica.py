import random
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

import httpx2

JsonObject = dict[str, Any]

MAX_RETRY_AFTER_SECONDS = 30.0


class UpstreamRequestFailed(Exception):
    pass


class UnretryableResponse(UpstreamRequestFailed):
    def __init__(self, status_code: int, url: str) -> None:
        super().__init__(f"{status_code} from {url}")
        self.status_code = status_code


class RetriesExhausted(UpstreamRequestFailed):
    pass


class MalformedResponse(UpstreamRequestFailed):
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
        last_attempt = self._backoff.attempts - 1
        for attempt in range(self._backoff.attempts):
            try:
                response = self._http.get(path, params=params)
            except httpx2.TransportError:
                retry_hint = None
            else:
                if response.status_code == 200:
                    return decode_json(response)
                if response.status_code != 429 and not response.is_server_error:
                    raise UnretryableResponse(response.status_code, str(response.request.url))
                retry_hint = retry_after(response)
            if attempt < last_attempt:
                self._sleep(self._backoff.delay(attempt, retry_hint, self._jitter()))
        raise RetriesExhausted(f"gave up after {self._backoff.attempts} attempts on {path}")


def decode_json(response: httpx2.Response) -> JsonObject:
    try:
        data: JsonObject = response.json()
    except ValueError as error:
        raise MalformedResponse(f"not JSON from {response.request.url}") from error
    return data


def retry_after(response: httpx2.Response) -> float | None:
    header = response.headers.get("Retry-After")
    if not header:
        return None
    try:
        seconds = float(header)
    except ValueError:
        try:
            seconds = (parsedate_to_datetime(header) - datetime.now(UTC)).total_seconds()
        except ValueError:
            return None
    return min(max(seconds, 0.0), MAX_RETRY_AFTER_SECONDS)
