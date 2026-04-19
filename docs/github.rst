######
GitHub
######

Overview
========

`GitHub <https://github.com>`__ is an online tool for software collaboration.

This :class:`~parsons.github.github.GitHub` class uses the `PyGitHub library <https://pygithub.readthedocs.io/en/latest/introduction.html>`_
to make requests to the `GitHub REST API <https://docs.github.com/en/rest>`__. The class provides methods to:

- Get an individual user, organization, repo, issue, or pull request
- Get lists of user or organization repos for a given ``username`` or ``organization_name``
- Get lists of repo issues, pull requests, and contributors for a given ``repo_name``
- Download files and tables

.. admonition:: API Credentials

   - If you have a GitHub account you can use your normal username and password to authenticate with the API.
   - You can also use `a personal access token <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens>`__.

Quickstart
==========

To instantiate the GitHub class using a username and password, you can store your username
and password as environmental variables (``GITHUB_USERNAME`` and ``GITHUB_PASSWORD``),
or pass them in as arguments. Alternatively, you can provide a personal access token as an
environmental variable (``GITHUB_ACCESS_TOKEN``) or as an argument.

.. code-block:: python
   :caption: Authenticate by passing a username and password arguments

   from parsons import GitHub
   github = GitHub(username='my_username', password='my_password')

.. code-block:: python
   :caption: Authenticate by passing an access token as an argument

   from parsons import GitHub
   github = GitHub(access_token='my_access_token')

.. code-block:: python
   :caption: Authenticate with environmental variables

   from parsons import GitHub
   github = GitHub()

With the class instantiated, you can now call various endpoints.

.. code-block:: python
   :caption: Get repo by its full name (account/name)

   parsons_repo = github.get_repo("move-coop/parsons")

.. code-block:: python
   :caption: Get the first page of a repo's issues as a Table

   parsons_issues_table = github.list_repo_issues("move-coop/parsons")

.. code-block:: python
   :caption: Download Parsons README.md to local "/tmp/README.md"

   parsons_readme_path = github.download_file("move-coop/parsons", "README.md", local_path="/tmp/README.md")

API
====

.. autoclass:: parsons.github.github.GitHub
   :inherited-members:
   :members:
