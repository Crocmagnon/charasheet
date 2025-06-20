##############################################
# write git info
##############################################
FROM alpine/git:2.49.0 AS git

WORKDIR /app
COPY .git /app/.git/
RUN git describe --tags --always > /git-describe
RUN git rev-parse HEAD > /git-commit
RUN date +'%Y-%m-%d %H:%M %Z' > /build-date



##############################################
# install python dependencies
##############################################
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev



##############################################
# Main image
##############################################
FROM python:3.13.3-slim-bookworm AS final

ARG DEBIAN_FRONTEND=noninteractive

# Setup user & group
##############################################
RUN groupadd -g 1000 django
RUN useradd -M -d /app -u 1000 -g 1000 -s /bin/bash django

# Setup system
##############################################
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        libxml2 \
        media-types

# Create directory structure
##############################################
COPY --from=builder --chown=django:django /app /app

RUN mkdir -p /app/data /app/db
RUN chown django:django /app /app/data /app/db

ENV STATIC_ROOT=/app/static
ENV SECRET_KEY "changeme"
ENV DEBUG "false"
ENV DATABASE_URL "sqlite:////app/db/db.sqlite3"

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/src
RUN python manage.py collectstatic --noinput --clear

# Copy git info
##############################################
COPY --chown=django:django --from=git /git-describe /git-commit /build-date /app/git/

EXPOSE 8000

WORKDIR /app/src

HEALTHCHECK --start-period=30s CMD python -c "import requests; requests.get('http://localhost:8000', timeout=2)"

USER django
CMD ["gunicorn", "charasheet.wsgi", "--graceful-timeout=5", "--worker-tmp-dir=/dev/shm", "--workers=2", "--threads=4", "--worker-class=gthread", "--bind=0.0.0.0:8000", "--log-file=-"]
