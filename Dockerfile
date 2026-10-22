FROM --platform=linux/amd64 python:3.11

###################
## Parsons setup ##
###################

# Refresh the OS trust store so system OpenSSL/curl do not trust the
# compromised eMudhra/emSign intermediates (see emudhra.we-have-a-problem.com).
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /src
COPY . /src/
WORKDIR /src

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install parsons. pyproject.toml floors certifi at 2026.10.19 (eMudhra/emSign CA
# incident); assert so a bad resolve fails the image build instead of shipping.
# uv.lock is gitignored, so this resolves from pyproject.toml at build time.
RUN uv sync --upgrade --all-extras --python python3.11 \
    && .venv/bin/python -c 'import certifi; assert [int(p) for p in certifi.__version__.split(".")] >= [2026, 10, 19], certifi.__version__'
ENV PATH="/src/.venv/bin:$PATH"

# The /app directory can house the scripts that will actually execute on this Docker image.
# Eg. If using this image in a Civis container script, Civis will install your script repo
# (from Github) to /app.
RUN mkdir /app
WORKDIR /app

# Useful for importing modules that are associated with your python scripts:
ENV PYTHONPATH=.:/app
