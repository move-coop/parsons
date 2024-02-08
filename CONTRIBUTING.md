We're thrilled that you're thinking about contributing to Parsons! Welcome to our contributor community.

You can find a detailed version of this guide [on our website](https://www.parsonsproject.org/pub/contributing-guide/).

The best way to get involved is by joining our Slack. To join, email engineering@movementcooperative.org. In addition to all the great discussions that happen on our Slack, we also have virtual events including trainings, pairing sessions, social hangouts, discussions, and more. Every other Thursday afternoon we host 🎉 Parsons Parties 🎉 on Zoom where we work on contributions together.

You can contribute by:

* [submitting issues](https://www.parsonsproject.org/pub/contributing-guide#submitting-issues)
* [contributing code](https://www.parsonsproject.org/pub/contributing-guide/)
* [updating our documentation](https://www.parsonsproject.org/pub/updating-documentation/)
* [teaching and mentoring](https://www.parsonsproject.org/pub/contributing-guide#teaching-and-mentoring)
* [helping "triage" issues and review pull requests](https://www.parsonsproject.org/pub/contributing-guide#maintainer-tasks)

We encourage folks to review existing issues before starting a new issue.

* If the issue you want exists, feel free to use the *thumbs up* emoji to up vote the issue.
* If you have additional documentation or context that would be helpful, please add using comments.
* If you have code snippets, but don’t have time to do the full write, please add to the issue!

We use labels to help us classify issues. They include:
* **bug** - something in Parsons isn’t working the way it should
* **enhancement** - new feature or request (e.g. a new API connector)
* **good first issue** - an issue that would be good for someone who is new to Parsons

## Contributing Code to Parsons

Generally, code contributions to Parsons will be either enhancements or bug requests (or contributions of [sample code](#sample-code), discussed below). All changes to the repository are made [via pull requests](#submitting-a-pull-request).

If you would like to contribute code to Parsons, please review the issues in the repository and find one you would like to work on. If you are new to Parsons or to open source projects, look for issues with the [**good first issue**](https://github.com/move-coop/parsons/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) label. Once you have found your issue, please add a comment to the issue that lets others know that you are interested in working on it. If you're having trouble finding something to work on, please ask us for help on Slack.

The bulk of Parsons is made up of Connector classes, which are Python classes that help move data in and out of third party services. When you feel ready, you may want to contribute by [adding a new Connector class](https://move-coop.github.io/parsons/html/build_a_connector.html).

### Making Changes to Parsons

To make code changes to Parsons, you'll need to set up your development environment, make your changes, and then submit a pull request.

To set up your development environment:

* Fork the Parsons project using [the “Fork” button in GitHub](https://guides.github.com/activities/forking/)
* Clone your fork to your local computer
* Set up a [virtual environment](#virtual-environments)
* Install the [dependencies](#installing-dependencies)
* Check that everything's working by [running the unit tests](#unit-tests) and the [linter](#linting)

Now it's time to make your changes. We suggest taking a quick look at our [coding conventions](#coding-conventions) - it'll make the review process easier down the line. In addition to any code changes, make sure to update the documentation and the unit tests if necessary. Not sure if your changes require test or documentation updates? Just ask in Slack or through a comment on the relevant issue.  When you're done, make sure to run the [unit tests](#unit-tests) and the [linter](#linting) again.

Finally, you'll want to [submit a pull request](#submitting-a-pull-request). And that's it!

#### Virtual Environments

If required dependencies conflict with packages or modules you need for other projects, you can create and use a [virtual environment](https://docs.python.org/3/library/venv.html).

```
python3 -m venv .venv       # Creates a virtual environment in the .venv folder
source .venv/bin/activate  # Activate in Unix or MacOS
.venv/Scripts/activate.bat # Activate in Windows
```

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

We use the [black](https://github.com/psf/black) and [flake8](http://flake8.pycqa.org/en/latest/) tools to [lint](https://en.wikipedia.org/wiki/Lint_(software)) the code in the repository to make sure it matches our preferred style. Both tools are installed as part of the Parsons dependencies.

Run the following commands from the root of the Parsons repository to lint your code changes:

```bash
> flake8 --max-line-length=100 --extend-ignore=E203,W503 parsons
> black parsons
```

Pre-commit hooks are available to enforce black and isort formatting on
commit. You can also set up your IDE to reformat using black and/or isort on
save.

To set up the pre-commit hooks, install pre-commit with `pip install
pre-commit`, and then run `pre-commit install`.

#### Coding Conventions

The following is a list of best practices to consider when writing code for the Parsons project:

* Each tool connector should be its own unique class (e.g. ActionKit, VAN) in its own Python package. Use existing connectors as examples when deciding how to layout your code.

* Methods should be named using a verb_noun structure, such as `get_activist()` or `update_event()`.

* Methods should reflect the vocabulary utilized by the original tool where possible to mantain transparency. For example, Google Cloud Storage refers to file like objects as blobs. The methods are called `get_blob()` rather than `get_file()`.

* Methods that can work with arbitrarily large data (e.g. database or API queries) should use of Parson Tables to hold the data instead of standard Python collections (e.g. lists, dicts).

* You should avoid abbreviations for method names and variable names where possible.

* Inline comments explaining complex codes and methods are appreciated.

* Capitalize the word Parsons for consistency where possible, especially in documentation.

If you are building a new connector or extending an existing connector, there are more best practices in the [How to Build a Connector](https://move-coop.github.io/parsons/html/build_a_connector.html) documentation.

## Documentation

Parsons documentation is built using the Python Sphinx tool. Sphinx uses the `docs/*.rst` files in the repository to create the documentation.

We have a [documentation label](https://github.com/move-coop/parsons/issues?q=is%3Aissue+is%3Aopen+label%3Adocumentation) that may help you find good docs issues to work on. If you are adding a new connector, you will need to add a reference to the connector to one of the .rst files. Please use the existing documentation as an example.

When editing documentation, make sure you are editing the source files (with .md or .rst extension) and not the build files (.html extension).

The workflow for documentation changes is a bit simpler than for code changes:

* Fork the Parsons project using [the “Fork” button in GitHub](https://guides.github.com/activities/forking/)
* Clone your fork to your local computer
* Change into the `docs` folder and install the requirements with `pip install -r requirements.txt` (you may want to set up a [virtual environment](#virtual-environments) first)
* Make your changes and re-build the docs by running `make html`. (Note: this builds only a single version of the docs, from the current files. To create docs with multiple versions like our publicly hosted docs, run `make deploy_docs`.)
* Open these files in your web browser to check that they look as you expect.
* [Submit a pull request](#submitting-a-pull-request)

When you make documentation changes, you only need to track the source files with git.  The docs built by the html folder should not be included.

You should not need to worry about the unit tests or the linter if you are making documentation changes only.

## Contributing Sample Code

One important way to contribute to the Parsons project is to submit sample code that provides recipes and patterns for how to use the Parsons library.

We have a folder called `useful_resources/` in the root of the repository. If you have scripts that incorporate Parsons, we encourage you to add them there!

The workflow for adding sample code is:

* Fork the Parsons project using [the “Fork” button in GitHub](https://guides.github.com/activities/forking/)
* Clone your fork to your local computer
* Add your sample code into the `useful_resources/` folder
* [Submit a pull request](#submitting-a-pull-request)

You should not need to worry about the unit tests or the linter if you are only adding sample code.

## Submitting a Pull Request

To submit a pull request, follow [these instructions to create a Pull Request from your fork](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork) back to the original Parsons repository.

The Parsons team will review your pull request and provide feedback. Please feel free to ping us if no one's responded to your Pull Request after a few days. We may not be able to review it right away, but we should be able to tell you when we'll get to it.

Once your pull request has been approved, the Parsons team will merge your changes into the Parsons repository
