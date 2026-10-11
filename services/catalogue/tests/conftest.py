import os
from collections.abc import Callable, Iterator

import httpx2
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from catalogue.infrastructure.jolpica import Backoff, JolpicaClient
from catalogue.infrastructure.settings import Settings

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


@pytest.fixture
def database_url() -> str:
    if "POSTGRES_PASSWORD" not in os.environ:
        pytest.skip("POSTGRES_* not set; run with: uv run --env-file .env pytest")
    return Settings().database_url


@pytest.fixture
def db_sessions(database_url: str) -> Iterator[sessionmaker[Session]]:
    engine = create_engine(database_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        yield sessionmaker(bind=connection, join_transaction_mode="create_savepoint")
        transaction.rollback()
