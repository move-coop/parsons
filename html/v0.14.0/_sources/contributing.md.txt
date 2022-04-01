## Submitting Issues

We encourage folks to review existing issues before starting a new issue.

* If the issue you want exists, feel free to use the *thumbs up* emoji to up vote the issue.
* If you have additional documentation or context that would be helpful, please add using comments.
* If you have code snippets, but don’t have time to do the full write, please add to the issue!

We use labels to help us classify issues. They include:
* **bug** - something in Parsons isn’t working the way it should
* **enhancement** - new feature or request (e.g. a new API connector)
* **good first issue** - an issue that would be good for someone who is new to Parsons

## Contributing Code to Parsons

Generally, code contributions to Parsons will fall into one of the following categories: bug fixes, enhancements, and sample code. All changes to the repository are made via pull requests.

### Figuring Out What to Contribute

If you would like to contribute to Parsons, please review the issues in the repository and find one you would like to work on. If you are new to Parsons or to open source projects, look for issues with the **good first issue** label. Once you have found your issue, please add a comment to the issue that lets others know that you are interested in working on it.

#### Sample Code

One important way to contribute to the Parsons project is to submit sample code that provides recipes and patterns for how to use the Parsons library.

We have a folder called `sample_code/` in the root of the repository. If you have scripts that incorporate Parsons, we encourage you to create a Pull Request adding them there!

### Coding Conventions

The following is a list of best practices to consider when writing code for the Parsons project:

* Each tool connector should be its own unique class (e.g. ActionKit, VAN) in its own Python package. Use existing connectors as examples when deciding how to layout your code.

* Methods should be named using a verb_noun structure, such as `get_activist()` or `update_event()`.

* Methods should reflect the vocabulary utilized by the original tool where possible to mantain transparency. For example, Google Cloud Storage refers to file like objects as blobs. The methods are called `get_blob()` rather than `get_file()`.

* Methods that can work with arbitrarily large data (e.g. database or API queries) should use of Parson Tables to hold the data instead of standard Python collections (e.g. lists, dicts).

* You should avoid abbreviations for method names and variable names where possible.

* Inline comments explaining complex codes and methods are appreciated.

### Documentation

Parsons documentation is built using the Python Sphinx tool. Sphinx uses the `docs/*.rst` files in the repository to create the documentation. If you are adding a new connector, you will need to add a reference to the connector to one of the .rst files. Please use the existing documentation as an example.

### Testing your Changes

The Parsons codebase uses automated unit tests and a linter to check for errors in the code and to ensure that the code is consistent with our preferred style. Before your changes can be merged, they will need to pass these checks.

#### Installing Dependencies

Before running or testing your code changes, be sure to install all of the required Python libraries that Parsons depends on.

From the root of the parsons repository, use the run the following command:

```bash
> pip install -r requirements.txt
```

#### Unit Tests

When contributing code, we ask you to add to tests that can be used to verify that the code is working as expected. All of our unit tests are located in the `test/` folder at the root of the repository.

We use the pytest tool to run our suite of automated unit tests. The pytest command line tool is installed as part of the Parsons dependencies.

To run all the entire suite of unit tests, execute the following command:

```bash
> pytest -rf test/
```

Once the pytest tool has finished running all of the tests, it will output details around any errors or test failures it encountered. If no failures are identified, then you are good to go!

**Note:*** Some tests are written to call out to external API’s, and will be skipped as part of standard unit testing. This is expected.

See the [pytest documentation](https://docs.pytest.org/en/latest/contents.html) for more info and many more options.

#### Linting

We use the [flake8](http://flake8.pycqa.org/en/latest/) tool to [lint](https://en.wikipedia.org/wiki/Lint_(software)) the code in the repository to make sure it matches our preferred style. The flake8 command line tool is installed as part of the Parsons dependencies.

Run the following command from the root of the Parsons repository to lint your code changes:

```bash
> flake8 --max-line-length=100 parsons
```

## Submitting a Pull Request

In order to contribute code changes to the Parsons repository, you will need to:

* Fork the Parsons project using [the “Fork” button in GitHub](https://guides.github.com/activities/forking/)
* Clone your fork to your local computer
* Make the necessary code changes
* Ensure your code changes pass the testing and linting checks described in this document
* Sync your changes to your Parsons fork
* [Create a Pull Request from your fork](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork) to the original Parsons repository
* The Parsons team will review your pull request and provide feedback
* Once your pull request has been approved, the Parsons team will merge your changes into the Parsons repository
