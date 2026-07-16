FROM --platform=linux/amd64 python:3.11@sha256:2ea01c83d3e1665a9ca4c5054dcd35c259c672fc5463b9f1a6200ca412a14f5c

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1

###################
## Parsons setup ##
###################

WORKDIR /src
COPY pyproject.toml setup.py ./
RUN uv sync --no-editable --all-extras --no-dev --python python3.11

COPY . /src/

ENV PATH="/src/.venv/bin:$PATH"
ENV PYTHONPATH=.:/app

# The /app directory can house the scripts that will actually execute on this Docker image.
# Eg. If using this image in a Civis container script,
# Civis will install your script repo (from Github) to /app.
RUN mkdir /app
WORKDIR /app

CMD ["python3"]
