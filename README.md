# Parsons


## About
Parsons, named after [Lucy Parsons](https://en.wikipedia.org/wiki/Lucy_Parsons), is a Python package that contains a growing list of connectors and integrations to move data between various tools. Parsons is focused on integrations and connectors for tools utilized by the progressive community.

Parsons is maintained by The Movement Cooperative. The Movement Cooperative is a member led organization focused on providing data, tools and strategic support for the progressive community.

Parsons is only compatible with Python 3.x

## Installation

Download this repository and then run `python setup.py develop`.

## Documentation
Our package documentation is hosted at [https://move-coop.github.io/parsons/html/index.html](https://move-coop.github.io/parsons/html/index.html). It is intended for developers _using_ Parsons.

The docs files are automatically built and deployed to that website as part of our CircleCI config.yml.

If you want to build the docs manually (eg. to test your updates locally):
- `cd docs/`
- `make html`
    - **Note**: This only creates html for files that have been modified. To create html for all files add the `-a` flag to `SPHINXOPTS    =` in Makefile.
- Open `docs/index.html` in your web browser.

Documentation for developers _working on_ Parsons should live in this README, rather than the hosted documentation website.

## Tests
Run all tests with this command:

``pytest -rf test/``

Run all tests in a file with:

``pytest -rf test/[test_some_module.py]``

Run test(s) with name(s) matching a string:

``pytest -rf -k [test_something]``

If you want to see all the console output for your tests (even those that pass), add the ``-s`` flag.

See the [pytest documentation](https://docs.pytest.org/en/latest/contents.html) for more info and many more options.

Many Parsons tests are built to hit a live server and will not run unless you set the environmental variable ``LIVE_TEST='TRUE'``

**Note**: We are in process of moving from python's native unittest system over to pytest. So you'll see tests written in both styles. The above pytest command will pull in both kinds of tests.

To "lint" the codebase to ensure it matches our preferred style:

``flake8 --max-line-length=100 parsons``

## Logging

Parsons uses the [native python logging system](https://docs.python.org/3/howto/logging.html). By default, log output will go to the console and look like:

```
parsons.modulename LOGLEVEL the specific log message
```

If you're writing a Parsons module, set up your logger at the top of the file, like this:

```python
import logging
logger = logging.getLogger(__name__)

# Then to use the logger:
# logger.info("processing a table")
```

## Best practices

### Table vs native python collection

When writing Parsons code, you'll often be faced with a choice of whether to store data in a Parsons Table or a native python collection (eg. list or dict). The general rule of thumb is use a Table when dealing with data that will make use of the ETL functionality Tables provide. Ie. If your data can be arbitrarily large, and/or if it has multiple fields per item (2D data), it is a good candidate for going into a Table. If your data is small and simple, eg. a list of files, we prefer simple python types like lists.
