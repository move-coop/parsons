GitHub
======

`GitHub <https://github.com>`_ is an online tool for software collaboration.

.. note::
   API Credentials
      - If you have a GitHub account you can use your normal username and password to authenticate with the API.
      - You can also use `a personal access token <https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token>`_.

**********
Quickstart
**********

**Get repo data**

.. code-block:: python

  from parsons import GitHub

  github = GitHub()

  # Get repo by its full name (account/name)
  parsons_repo = github.get_repo("move-coop/parsons")

**Get repo issues in a ``Table``**

.. code-block:: python

  from parsons import GitHub

  github = GitHub()

  # Get the first page of a repo's issues as a Table
  parsons_issues_table = github.list_repo_issues("move-coop/parsons")

**Download the contents of a repo file**

.. code-block:: python

  from parsons import GitHub

  github = GitHub()

  # Download Parsons README.md to local "/tmp/README.md"
  parsons_readme_path = github.download_file("move-coop/parsons", "README.md", local_path="/tmp/README.md")

===
API
===
.. autoclass:: parsons.GitHub
   :inherited-members:
