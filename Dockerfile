FROM --platform=linux/amd64 python:3.11

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
