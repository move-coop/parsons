#########################
## Image Configuration ##
#########################
FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:sha256:015fe7b33cea4a9a0a2fcda085cbfa3fa03419f973ff1b6a3e337edde48ba9ff
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot
WORKDIR /app

###########################################
## UV / Python Environment Configuration ##
###########################################
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin

#############################
## Dependency Installation ##
#############################
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --all-extras
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --all-extras
ENV PATH="/app/.venv/bin:$PATH"

#############
## Startup ##
#############
ENTRYPOINT []
USER nonroot
CMD ["python3"]
