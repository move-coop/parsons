FROM --platform=linux/amd64 python:3.11

###################
## Parsons setup ##
###################

RUN mkdir /src

RUN pip install uv
RUN uv pip install --system .[all]

COPY . /src/
WORKDIR /src

RUN python setup.py develop

# The /app directory can house the scripts that will actually execute on this Docker image.
# Eg. If using this image in a Civis container script, Civis will install your script repo
# (from Github) to /app.
RUN mkdir /app
WORKDIR /app
# Useful for importing modules that are associated with your python scripts:
ENV PYTHONPATH=.:/app
