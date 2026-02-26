GitHub
======

********
Overview
********

`GitHub <https://github.com>`_ is an online tool for software collaboration.

This ``GitHub`` class uses the `PyGitHub library <https://pygithub.readthedocs.io/en/latest/introduction.html>`_
to make requests to the `GitHub REST API <https://docs.github.com/en/rest>`_. The class provides methods to:

- Get an individual user, organization, repo, issue, or pull request
- Get lists of user or organization repos for a given ``username`` or ``organization_name``
- Get lists of repo issues, pull requests, and contributors for a given ``repo_name``
- Download files and tables

.. note::

   API Credentials
      - If you have a GitHub account you can use your normal username and password to authenticate with the API.
      - You can also use `a personal access token <https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token>`_.

**********
Quickstart
**********

To instantiate the GitHub class using a username and password, you can store your username
and password as environmental variables (``GITHUB_USERNAME`` and ``GITHUB_PASSWORD``),
or pass them in as arguments. Alternatively, you can provide a personal access token as an
environmental variable (``GITHUB_ACCESS_TOKEN``) or as an argument.

.. code-block:: python

  from parsons import GitHub

  # Authenticate by passing a username and password arguments
  github = GitHub(username='my_username', password='my_password')

  # Authenticate by passing an access token as an argument
  github = GitHub(access_token='my_access_token')

  # Authenticate with environmental variables
  github = GitHub()

With the class instantiated, you can now call various endpoints.

.. code-block:: python

  # Get repo by its full name (account/name)
  parsons_repo = github.get_repo("move-coop/parsons")

  # Get the first page of a repo's issues as a Table
  parsons_issues_table = github.list_repo_issues("move-coop/parsons")

  # Download Parsons README.md to local "/tmp/README.md"
  parsons_readme_path = github.download_file("move-coop/parsons", "README.md", local_path="/tmp/README.md")

***
API
***

.. autoclass:: parsons.github.github.GitHub
   :inherited-members:
   :members:
   