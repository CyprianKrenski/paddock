FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
ARG SERVICE

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
COPY services/catalogue/pyproject.toml services/catalogue/
COPY services/analysis/pyproject.toml services/analysis/
COPY services/web/pyproject.toml services/web/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-workspace --package "${SERVICE}"

COPY services/${SERVICE}/ services/${SERVICE}/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package "${SERVICE}"

ENV PATH="/app/.venv/bin:$PATH" SERVICE=${SERVICE}
USER 65532
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn ${SERVICE}.main:from_env --factory --host 0.0.0.0 --port 8000"]
