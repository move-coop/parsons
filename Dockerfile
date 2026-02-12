FROM --platform=linux/amd64 python:3.11

####################
## Selenium setup ##
####################

# TODO Remove when we have a TMC-specific Docker image

# Much of this was pulled from examples at https://github.com/joyzoursky/docker-python-chromedriver

# install google chrome
RUN   wget -qO- https://dl.google.com/linux/linux_signing_key.pub \
    | gpg --dearmor -o /etc/apt/keyrings/google.gpg; \
  chmod 0644 /etc/apt/keyrings/google.gpg; \
  echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/google.gpg] https://dl.google.com/linux/chrome/deb/ stable main' \
    > /etc/apt/sources.list.d/google-chrome.list
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

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
