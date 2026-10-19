from collections.abc import Callable

import httpx2
import pytest

from catalogue.infrastructure.jolpica import Backoff, JolpicaClient

Handler = Callable[[httpx2.Request], httpx2.Response]


@pytest.fixture
def sleeps() -> list[float]:
    return []


@pytest.fixture
def make_client(sleeps: list[float]) -> Callable[[Handler], JolpicaClient]:
    def build(handler: Handler) -> JolpicaClient:
        http = httpx2.Client(
            base_url="https://api.jolpi.ca/ergast/f1",
            headers={"User-Agent": "paddock/0.1"},
            transport=httpx2.MockTransport(handler),
        )
        return JolpicaClient(
            http,
            backoff=Backoff(attempts=4, base_seconds=0.5),
            sleep=sleeps.append,
            jitter=lambda: 0.5,
        )

    return build
