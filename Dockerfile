FROM --platform=linux/amd64 python:3.7

####################
## Selenium setup ##
####################

# TODO Remove when we have a TMC-specific Docker image

# Much of this was pulled from examples at https://github.com/joyzoursky/docker-python-chromedriver

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

###################
## Parsons setup ##
###################

RUN mkdir /src

COPY requirements.txt /src/
RUN pip install -r /src/requirements.txt

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
