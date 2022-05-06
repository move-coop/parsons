# Parsons
[![Downloads](https://pepy.tech/badge/parsons)](https://pepy.tech/project/parsons)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/parsons)](https://pypi.org/project/parsons/)
[![PyPI](https://img.shields.io/pypi/v/parsons?color=blue)](https://pypi.org/project/parsons/)
[![CircleCI](https://circleci.com/gh/move-coop/parsons/tree/main.svg?style=shield)](https://circleci.com/gh/move-coop/parsons/tree/main)

A Python package that provides a simple interface to a variety of utilities and tools frequently used by progressive organizations, political and issue campaigns, activists, and other allied actors.

Parsons offers simplified interactions with these services and tools, including a growing number of CRMs, organizing tools, cloud compute service providers, as well as tools to easily transform data in transit.

This project is maintained by [The Movement Cooperative](https://movementcooperative.org/) and is named after [Lucy Parsons](https://en.wikipedia.org/wiki/Lucy_Parsons). The Movement Cooperative is a member-led organization focused on providing data, tools, and strategic support for the progressive community.

Parsons is only compatible with Python 3.7-10

## Table of Contents
- [License and Usage](#license-and-usage)
- [Documentation](#documentation)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Community](#community) 

## License and Usage
Usage of Parsons is governed by a [modified Apache License with author attribution statement](https://github.com/move-coop/parsons/blob/main/LICENSE.md).

## Documentation
To gain a full understanding of all of the features of Parsons, please review the Parsons [documentation](https://move-coop.github.io/parsons/html/index.html).

## Installation


### PYPI
You can install the most recent release by running: `pip install parsons[all]`


### Install from Github

To access the most recent code base that may contain features not yet included in the latest release, download this repository and then run `python setup.py develop`.

### Docker Container
We have a Parsons Docker container hosted on [DockerHub](https://cloud.docker.com/u/movementcooperative/repository/docker/movementcooperative/parsons) for each release of Parsons, including the `latest`.

## Quickstart

For this Quickstart, we are looking to generate a list of voters with cell phones using a [dummy data file](docs/quickstart.csv). We use the `assert` statements to verify that the data has been loaded correctly.

```python
# Download the Census data from the Parsons GitHub repository
from parsons import GitHub
github = GitHub()
dummy_data = github.download_table('move-coop/parsons', 'docs/quickstart.csv')
assert dummy_data.num_rows == 1000  # Check that we got all 1,000 people

# Filter down to people with cell phones
people_with_cell_phones = dummy_data.select_rows(lambda row: row['is_cell'] == 'true')
assert people_with_cell_phones.num_rows == 498  # Check that we filtered down to our 498 people

# Extract only the columns we need (first name, last name, phone number)
people_with_cell_phones = people_with_cell_phones.cut('first_name', 'last_name', 'phone_number')
assert people_with_cell_phones.columns == ['first_name', 'last_name', 'phone_number'] # Check columns

# Output the list to a local CSV file
filename = people_with_cell_phones.to_csv()  # filename will be the path to the local CSV file

# In order to upload data to a Google Sheet, you will need to set the GOOGLE_DRIVE_CREDENTIALS
# environment variable
from parsons import GoogleSheets
sheets = GoogleSheets()
sheet_id = sheets.create_spreadsheet('Voter Cell Phones')
sheets.append_to_sheet(sheet_id, people_with_cell_phones)
```

## Community
We hope to foster a strong and robust community of individuals who use and contribute to further development. Individuals are encouraged to submit issues with bugs, suggestions and feature requests. [Here](https://github.com/move-coop/parsons/blob/main/CONTRIBUTING.md) are the guidelines and best practices for contributing to Parsons.

You can also stay up to date by joining the Parsons Slack group, an active community of Parsons contributors and progressive data engineers. For an invite, just reach out to engineering+parsons@movementcooperative.org!
