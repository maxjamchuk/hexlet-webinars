FROM ghcr.io/astral-sh/uv:0.8.13 AS uv

FROM python:3.12-slim

COPY --from=uv /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

CMD ["sh", "-c", "uv run alembic upgrade head && uv run fastapi run app/main.py --host 0.0.0.0 --port 8000"]
