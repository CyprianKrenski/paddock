# paddock

Replay of past Formula 1 races, built as microservices for the BTH course PA2577.

## Local development

```bash
cp .env.example .env            # then fill in POSTGRES_PASSWORD
uv sync
docker compose up -d postgres
uv run --env-file .env alembic -c services/catalogue/alembic.ini upgrade head
uv run --env-file .env pytest -q          # integration tests included
uv run pytest -q                          # unit tests only, integration skipped
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run --env-file .env uvicorn catalogue.main:create_app --factory --port 8001
```
