###########################################
## Setup Environment
###########################################
FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:e1726dc72f5a45d6fde5814c9bdb87cfdf46ea4fd8a5fd806fdda378fffb4ae5 AS builder
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1

RUN --mount=type=cache,target=/root/.cache/uv \
    # --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --all-extras # --locked

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-extras --no-editable # --locked

###########################################
## Simplify Runtime Image
###########################################
FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:e1726dc72f5a45d6fde5814c9bdb87cfdf46ea4fd8a5fd806fdda378fffb4ae5

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
