FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
   UV_LINK_MODE=copy \
   UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
   --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
   --mount=type=bind,source=uv.lock,target=uv.lock \
   uv sync --locked --no-install-project --no-dev

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
   uv sync --locked --no-dev

FROM python:3.12-slim-bookworm AS runtime

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

COPY --from=builder --chown=app:app /app /app

RUN printf '#!/bin/bash\n' > runner.sh \
   && printf 'set -e\n' >> runner.sh \
   && printf 'echo "Running Alembic migrations..."\n' >> runner.sh \
   && printf 'alembic upgrade head\n' >> runner.sh \
   && printf 'echo "Starting Gunicorn..."\n' >> runner.sh \
   && printf 'exec gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --workers 2 --bind 0.0.0.0:8000 --keep-alive 75 --timeout 120\n' >> runner.sh \
   && chmod +x /app/runner.sh

ENV PATH="/app/.venv/bin:$PATH"

USER app

EXPOSE 8000

ENTRYPOINT ["/app/runner.sh"]