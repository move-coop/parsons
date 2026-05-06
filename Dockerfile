FROM --platform=linux/amd64 python:3.11@sha256:5062f6c22a2c3b8b3717c642af3852310d9a81c3c2c0fc72449a9a79ef09ae63

###################
## Parsons setup ##
###################

RUN mkdir /src
COPY . /src/
WORKDIR /src

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install parsons
RUN uv sync --upgrade --all-extras --python python3.11
ENV PATH="/src/.venv/bin:$PATH"

# The /app directory can house the scripts that will actually execute on this Docker image.
# Eg. If using this image in a Civis container script, Civis will install your script repo
# (from Github) to /app.
RUN mkdir /app
WORKDIR /app

# Useful for importing modules that are associated with your python scripts:
ENV PYTHONPATH=.:/app
