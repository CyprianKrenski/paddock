# paddock

Replay of past Formula 1 races, built as microservices for the BTH course PA2577.

## Local development

```bash
uv sync
uv run pytest -q
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run uvicorn catalogue.main:create_app --factory --port 8001
```
