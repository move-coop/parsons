# Parsons


A Python package that provides a simple interface to a variety of utilities and tools frequently used by progressive organizations, political and issue campaigns, activists, and other allied actors.

Parsons offers simplified interactions with these services and tools, including a growing number of CRMs, organizing tools, cloud compute service providers, as well as tools to easily trasform data in transit.

This project maintained by [The Movement Cooperative](https://movementcooperative.org/) and is named after [Lucy Parsons](https://en.wikipedia.org/wiki/Lucy_Parsons). The Movement Cooperative is a member led organization focused on providing data, tools, and strategic support for the progressive community.


### Quickstart 
```
Examples with common tools
```


### Installation


#### PYPI
You can install the most recent version by running: `pip install parsons`


#### Install from GitHub
[INSTRUCTIONS HERE]


### Community
We hope to foster a strong and robust community of individuals who use and contribute to further development. Individuals are encouraged to submit issues with bugs, suggestions and feature requests.

You can also stay up to date by joining the parsons google group [DROP IN LINK]


_**CONSIDER MOVING CONTRIBUTION NOTES BELOW TO ANOTHER MD**_

## Contributing To Parsons
We welcome and encourage anyone to contribute to Parsons. Any new features should include full documentation and tests to ensure the stability of the code.

Below, please find notes on how contribute to Parsons:


### Documentation
The docs files are automatically built and deployed to that website as part of our CircleCI config.yml. You should not need to manually update the documents in most instances.

If you need to build the docs manually (eg. to test your updates locally):
- `cd docs/`
- `make html`
    - **Note**: This only creates html for files that have been modified. To create html for all files add the `-a` flag to `SPHINXOPTS    =` in Makefile.
- Open `docs/index.html` in your web browser.

Documentation for developers _working on_ Parsons should live in this README, rather than the hosted documentation website.

### Tests
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

### Logging

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

### Best practices

#### Table vs native python collection

When writing Parsons code, you'll often be faced with a choice of whether to store data in a Parsons Table or a native python collection (eg. list or dict). The general rule of thumb is use a Table when dealing with data that will make use of the ETL functionality Tables provide. Ie. If your data can be arbitrarily large, and/or if it has multiple fields per item (2D data), it is a good candidate for going into a Table. If your data is small and simple, eg. a list of files, we prefer simple python types like lists.

#### Coding Conventions

* Each tool should be its own unique class (e.g. ActionKit, VAN)

* Methods should be named using a verb_noun structure, such as `get_activist()` or `update_event()`. 

* Methods should reflect the vocabulary utilized by the original tool where possible to mantain transparency. For example, Google Cloud Storage refers to file like objects as blobs. The methods are called `get_blob` rather than `get_file()`.

* You should avoid abbreviations for methods and variables where possible.

* Inline comments explaining complex codes and methods are appreciated.
