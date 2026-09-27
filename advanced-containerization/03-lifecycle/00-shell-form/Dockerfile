# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:0.8.13 AS uv
FROM python:3.12-slim
COPY --from=uv /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY app ./app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000
