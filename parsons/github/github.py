import itertools
import logging
from datetime import date, datetime
from functools import partial, wraps
from pathlib import Path
from typing import Any, Literal

import petl
import requests
from github import Auth as PyGithubAuth
from github import Github as PyGithub
from github.GithubException import UnknownObjectException
from github.PaginatedList import PaginatedList

from parsons.etl.table import Table
from parsons.utilities import check_env, files

logger = logging.getLogger(__name__)


def _wrap_method(decorator, method):
    @wraps(method)
    def _wrapper(self, *args, **kwargs):
        bound_method = partial(method.__get__(self, type(self)))
        return decorator(bound_method)(*args, **kwargs)

    return _wrapper


def decorate_methods(decorator):
    # Based on Django's django.utils.decorators.method_decorator
    def decorate(cls):
        for method in dir(cls):
            # Don't decorate dunder methods
            if method.startswith("__"):
                continue
            cls_method = getattr(cls, method)
            if callable(cls_method):
                setattr(cls, method, _wrap_method(decorator, cls_method))
        return cls

    return decorate


def wrap_github_404(func):
    @wraps(func)
    def _wrapped_func(*args, **kwargs):
        try:
            return (func)(*args, **kwargs)
        except UnknownObjectException as e:
            raise ParsonsGitHubError(
                "Couldn't find the object you referenced, maybe you need to log in?"
            ) from e

    return _wrapped_func


class ParsonsGitHubError(Exception):
    pass


@decorate_methods(wrap_github_404)
class GitHub:
    """
    Creates a GitHub class for accessing the GitHub API.

    Uses :mod:`parsons.utilities.check_env` to load credentials
    from environment variables if not supplied.
    Supports either a username and password or an access token for authentication.
    The client also supports unauthenticated access.

    Args:
        username:
            Username of account to use for credentials.
            Can be set with ``GITHUB_USERNAME`` environment variable.
        password:
            Password of account to use for credentials.
            Can be set with ``GITHUB_PASSWORD`` environment variable.
        access_token:
            Access token to use for credentials.
            Can be set with ``GITHUB_ACCESS_TOKEN`` environment variable.

    """

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
    ) -> None:
        self.username = check_env.check("GITHUB_USERNAME", username, optional=True)
        self.password = check_env.check("GITHUB_PASSWORD", password, optional=True)
        self.access_token = check_env.check("GITHUB_ACCESS_TOKEN", access_token, optional=True)

        if self.username and self.password:
            self.client = PyGithub(
                auth=PyGithubAuth.Login(login=self.username, password=self.password)
            )
        elif self.access_token:
            self.client = PyGithub(auth=PyGithubAuth.Token(token=self.access_token))
        else:
            self.client = PyGithub()

    def _as_table(
        self, paginated_list: PaginatedList, page: int | None = None, page_size: int = 100
    ) -> Table:
        """
        Converts a paginated list into a Parsons :ref:`Table`.

        Uses the ``_rawData`` property of each item instead of
        calling ``raw_data`` to avoid making a separate request for each item
        in a page for types that PyGithub doesn't consider complete.

        Args:
            paginated_list: PyGithub paginated list object.
            page:
                Page number to load.
                If not specified, all results are returned.
            page_size:
                Page size.
                Ignored if `page` is not set.

        Returns:
            Table of list data

        """
        stream = (item._rawData for item in paginated_list)

        if page is not None:
            start = (page - 1) * page_size
            stop = start + page_size
            stream = itertools.islice(stream, start, stop)

        return Table(list(stream))

    def get_user(self, username: str) -> dict[str, Any]:
        """
        Loads a GitHub user by username.

        Args:
            username: Username of user to load.

        Returns:
            User information

        """
        return self.client.get_user(username).raw_data

    def get_organization(self, organization_name) -> dict[str, Any]:
        """
        Loads a GitHub organization by name.

        Args:
            organization_name: Name of organization to load

        Returns:
            Organization information

        """
        return self.client.get_organization(organization_name).raw_data

    def get_repo(self, repo_name: str) -> dict[str, Any]:
        """
        Loads a GitHub repo by name.

        Args:
            repo_name: Full repo name (account/name)

        Returns:
            Repo information

        """
        return self.client.get_repo(repo_name).raw_data

    def list_user_repos(
        self, username: str, page: int | None = None, page_size: int = 100
    ) -> Table:
        """
        List user repos with pagination, returning a :ref:`Table`.

        Args:
            username: GitHub username
            page:
                Page number.
                All results are returned if not set.
            page_size: Page size

        Returns:
            Table with page of user repos

        """
        logger.info(f"Listing page {page} of repos for user {username}")

        return self._as_table(
            self.client.get_user(username).get_repos(), page=page, page_size=page_size
        )

    def list_organization_repos(
        self, organization_name: str, page: int | None = None, page_size: int = 100
    ) -> Table:
        """
        List organization repos with pagination, returning a :ref:`Table`.

        Args:
            organization_name: GitHub organization name
            page:
                Page number.
                All results are returned if not set.
            page_size: Page size

        Returns:
            Table with page of organization repos

        """
        logger.info(f"Listing page {page} of repos for organization {organization_name}")

        return self._as_table(
            self.client.get_organization(organization_name).get_repos(),
            page=page,
            page_size=page_size,
        )

    def get_issue(self, repo_name: str, issue_number: int) -> dict[str, Any]:
        """
        Loads a GitHub issue.

        Args:
            repo_name: Full repo name (account/name)
            issue_number: Number of issue to load

        Returns:
            Issue information

        """
        return self.client.get_repo(repo_name).get_issue(number=issue_number).raw_data

    def list_repo_issues(
        self,
        repo_name: str,
        state: Literal["open", "closed", "all"] = "open",
        assignee: str | None = None,
        creator: str | None = None,
        mentioned: str | None = None,
        labels: list[str] | None = None,
        sort: Literal["created", "updated", "comments"] = "created",
        direction: Literal["asc", "desc"] = "desc",
        since: datetime | date | None = None,
        page: int | None = None,
        page_size: int = 100,
    ) -> Table:
        """
        List issues for a given repo.

        Args:
            repo_name: Full repo name (account/name)
            state: State of issues to return.
            assignee: Name of assigned user, "none", or "*".
            creator: Name of user that created the issue.
            mentioned: Name of user mentioned in the issue.
            labels:
                List of label names.
                Defaults to []
            sort: What to sort results by.
            direction: Direction to sort.
            since: Timestamp to pull issues since.
            page:
                Page number.
                All results are returned if not set.
            page_size: Page size.

        Returns:
            Table with page of repo issues

        """
        if labels is None:
            labels = []

        logger.info(f"Listing page {page} of issues for repo {repo_name}")

        kwargs_dict: dict[str, Any] = {"state": state, "sort": sort, "direction": direction}
        if assignee:
            kwargs_dict["assignee"] = assignee
        if creator:
            kwargs_dict["creator"] = self.client.get_user(creator)
        if mentioned:
            kwargs_dict["mentioned"] = mentioned
        if len(labels) > 0:
            kwargs_dict["labels"] = ",".join(labels)
        if since:
            kwargs_dict["since"] = f"{since.isoformat()[:19]}Z"

        return self._as_table(
            self.client.get_repo(repo_name).get_issues(**kwargs_dict),
            page=page,
            page_size=page_size,
        )

    def get_pull_request(self, repo_name: str, pull_request_number: int) -> dict[str, Any]:
        """
        Loads a GitHub pull request.

        Args:
            repo_name: Full repo name (account/name)
            pull_request_number: Pull request number

        Returns:
            Pull request information

        """
        return self.client.get_repo(repo_name).get_pull(pull_request_number).raw_data

    def list_repo_pull_requests(
        self,
        repo_name: str,
        state: Literal["open", "closed", "all"] = "open",
        base: str | None = None,
        sort: Literal["created", "updated", "popularity"] = "created",
        direction: Literal["asc", "desc"] = "desc",
        page: int | None = None,
        page_size: int = 100,
    ) -> Table:
        """
        Lists pull requests for a given repo.

        Args:
            repo_name: Full repo name (account/name)
            state: Current state of the pull request.
            base: Base branch to filter pull requests by.
            sort: How to sort pull requests.
            direction: Direction to sort by.
            page:
                Page number.
                All results are returned if not set.
            page_size: Page size.

        Returns:
            Table with page of repo pull requests

        """
        logger.info(f"Listing page {page} of pull requests for repo {repo_name}")

        kwargs_dict = {"state": state, "sort": sort, "direction": direction}
        if base:
            kwargs_dict["base"] = base

        return self._as_table(
            self.client.get_repo(repo_name).get_pulls(**kwargs_dict),
            page=page,
            page_size=page_size,
        )

    def list_repo_contributors(
        self, repo_name: str, page: int | None = None, page_size: int = 100
    ) -> Table:
        """
        Lists contributors for a given repo.

        Args:
            repo_name: Full repo name (account/name)
            page:
                Page number.
                All results are returned if not set.
            page_size: Page size.

        Returns:
            Table with page of repo contributors

        """
        logger.info(f"Listing page {page} of contributors for repo {repo_name}")

        return self._as_table(
            self.client.get_repo(repo_name).get_contributors(),
            page=page,
            page_size=page_size,
        )

    def download_file(
        self, repo_name: str, path: str, branch: str | None = None, local_path: str | None = None
    ) -> str | None:
        """Download a file from a repo by path and branch. Defaults to the repo's default branch if
        branch is not supplied.

        Uses the download_url directly rather than the API because the API only supports contents up
        to 1MB from a repo directly, and the process for downloading larger files through the API is
        much more involved.

        Because download_url does not go through the API, it does not support username / password
        authentication, and requires a token to authenticate.

        Args:
            repo_name: Full repo name (account/name)
            path: Path from the repo base directory
            branch:
                Branch to download file from.
                Defaults to repo default branch
            local_path:
                Local file path to download file to.
                Will create a temp file if not supplied.

        Returns:
            File path of downloaded file

        Raises:
            github.GithubException.UnknownObjectException: The requested object could not be found (404 Error).
            ParsonsGitHubError: An error occurred while downloading a file.

        """
        if not local_path:
            local_path = files.create_temp_file_for_path(path)

        repo = self.client.get_repo(repo_name)
        if branch is None:
            branch = repo.default_branch

        logger.info(f"Downloading {path} from {repo_name}, branch {branch} to {local_path}")

        headers = None
        if self.access_token:
            headers = {
                "Authorization": f"token {self.access_token}",
            }

        res = requests.get(
            f"https://raw.githubusercontent.com/{repo_name}/{branch}/{path}",
            headers=headers,
        )
        if res.status_code == 404:
            raise UnknownObjectException(status=404, data=res.content)
        elif res.status_code != 200:
            raise ParsonsGitHubError(
                f"Error downloading {path} from repo {repo_name}: {res.content}"
            )

        Path(local_path).write_bytes(res.content)

        logger.info(f"Downloaded {path} to {local_path}")
        return local_path

    def download_table(
        self,
        repo_name: str,
        path: str,
        branch: str | None = None,
        local_path: str | None = None,
        delimiter: str = ",",
    ) -> Table:
        """
        Download a CSV file from a repo by path and branch as a Parsons :ref:`Table`.

        Args:
            repo_name: Full repo name (account/name)
            path: Path from the repo base directory
            branch:
                Branch to download file from.
                Defaults to repo default branch
            local_path:
                Local file path to download file to.
                Will create a temp file if not supplied.
            delimiter:
                The CSV delimiter to use to parse the data.

        """
        downloaded_file = self.download_file(repo_name, path, branch, local_path)

        return Table(petl.fromcsv(downloaded_file, delimiter=delimiter))
