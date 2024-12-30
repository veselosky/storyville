# First, build the application in the `/app` directory using uv.
ARG PYTHON_VERSION=3.12
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
# For good layer caching, create the virtualenv before copying the source code
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
# Production image doesn't need tests or other stuff at top level (but it DOES
# need the REAMDE.md because it's referenced in pyproject.toml)
COPY ./README.md /app/
COPY ./src/ /app/

# Install the app itself
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev

# TODO If using i18n, compile the translations with the compilemessages command

################################################################################
# Then, use a final image without uv
FROM python:${PYTHON_VERSION}-slim-bookworm
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

RUN useradd -r -U app
# Declare volumes that need to be mounted from the host. `db` holds the SQLite
# database, and `www` holds static files and uploaded media to be served by the
# web server.
VOLUME ["/app/var/db", "/app/var/www"]

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=storyville.settings

# Switch to the app user
USER app

# Add metadata
LABEL org.opencontainers.image.source=https://github.com/veselosky/storyville

# Use Granian to run the application
EXPOSE 8000
CMD ["granian", "--interface", "wsgi", "--workers", "4", "--host", "0.0.0.0", "storyville.wsgi:application"]
