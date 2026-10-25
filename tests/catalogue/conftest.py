import os
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from catalogue.infrastructure.settings import Settings


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
