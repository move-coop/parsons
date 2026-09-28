###########################################
## Setup Environment
###########################################
FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:4bf4ce1c06fbeecaf116c05f85916a3264807d47694f3ffc09ca0ddf952348ea AS builder
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --all-extras

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --all-extras --no-editable

###########################################
## Simplify Runtime Image
###########################################
FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:4bf4ce1c06fbeecaf116c05f85916a3264807d47694f3ffc09ca0ddf952348ea

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv

###########################################
## Startup ##
###########################################

ENTRYPOINT []
USER nonroot
CMD ["python3"]
