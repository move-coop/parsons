import itertools
import logging
from collections.abc import Callable
from datetime import date, datetime
from functools import wraps
from http import HTTPStatus
from pathlib import Path
from typing import Any, Literal, ParamSpec, TypeVar, overload

import petl
import requests
from github import Auth as PyGithubAuth
from github import Github as PyGithub
from github import PaginatedList as PyGithubPaginatedList
from github.GithubException import UnknownObjectException

from parsons.etl.table import Table
from parsons.utilities import check_env, files
from parsons.utilities.bearer_auth import BearerAuth

logger = logging.getLogger(__name__)

P = ParamSpec("P")  # parameter
R = TypeVar("R")  # return type
T = TypeVar("T", bound=type)  # class


@overload
def wrap_github_404(target: T) -> T: ...


@overload
def wrap_github_404(target: Callable[P, R]) -> Callable[P, R]: ...


def wrap_github_404(target: Callable[P, R] | T) -> Callable[P, R] | T:
    """
    Catch GitHub UnknownObjectException errors and raise a ParsonsGitHubError instead.

    Can be used as a decorator on a single function or an entire class.

    """
    if isinstance(target, type):  # Decorate all methods when used on a class
        for name in dir(target):
            if name.startswith("__"):
                continue
            attr = getattr(target, name)
            if callable(attr) and not isinstance(attr, (type, property)):
                setattr(target, name, wrap_github_404(attr))
        return target

    @wraps(target)
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # Handle use on a single function/metohd
        """Catch UnknownObjectException from GitHub API calls and raise ParsonsGitHubError."""
        try:
            return target(*args, **kwargs)
        except UnknownObjectException as e:
            err_msg = "Couldn't find the object you referenced, maybe you need to log in?"
            raise ParsonsGitHubError(err_msg) from e

    return _wrapper


class ParsonsGitHubError(Exception):
    """Exception class for errors encountered by the Parsons GitHub connector."""


@wrap_github_404
class GitHub:
    """Parsons connector for interacting with GitHub endpoints."""

    access_token: str | None = None

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
    ) -> None:
        """
        Instantiate the GitHub class.

        Supports authticated use with either a username and password
        or an access token, along with unauthenticated access.

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
        auth = None
        if (username := check_env.check("GITHUB_USERNAME", username, optional=True)) and (
            password := check_env.check("GITHUB_PASSWORD", password, optional=True)
        ):
            auth = PyGithubAuth.Login(login=username, password=password)
        elif access_token := check_env.check("GITHUB_ACCESS_TOKEN", access_token, optional=True):
            auth = PyGithubAuth.Token(token=access_token)
        self.client = PyGithub(auth=auth)

    def _as_table(
        self,
        paginated_list: PyGithubPaginatedList.PaginatedList,
        page: int | None = None,
        page_size: int = 100,
    ) -> Table:
        """
        Convert a list into a :ref:`Table`.

        Pagination is supported via `page` and `page_size`.

        Uses the ``_rawData`` property of each item instead of the ``raw_data`` property
        to avoid making a separate request for each item in a page for types that
        `PyGithub` doesn't consider complete.

        Args:
            paginated_list: PyGithub paginated list
            page:
                Page number to load.
                If not specified, all results are returned.
            page_size:
                Page size.
                Ignored if `page` is not set.

        Returns:
            Raw data of the list as a :ref:`Table`.

        """
        stream = (item._rawData for item in paginated_list)

        if page is not None:
            start = (page - 1) * page_size
            stop = start + page_size
            stream = itertools.islice(stream, start, stop)

        return Table(list(stream))

    def get_user(self, username: str) -> dict[str, Any]:
        """
        Load a GitHub user by username.

        Args:
            username: Username of user to load

        Returns:
            User information

        """
        return self.client.get_user(username).raw_data

    def get_organization(self, organization_name: str) -> dict[str, Any]:
        """
        Load a GitHub organization by name.

        Args:
            organization_name: Name of organization to load

        Returns:
            Organization information

        """
        return self.client.get_organization(organization_name).raw_data

    def get_repo(self, repo_name: str) -> dict[str, Any]:
        """
        Load a GitHub repo by name.

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
        List user repos.

        Pagination is supported via `page` and `page_size`.

        Args:
            username: GitHub username
            page:
                Page number to load.
                If not specified, all results are returned.
            page_size:
                Page size.
                Ignored if `page` is not set.

        """
        logger.info("Listing page %s of repos for user %s", page, username)

        return self._as_table(
            self.client.get_user(username).get_repos(), page=page, page_size=page_size
        )

    def list_organization_repos(
        self, organization_name: str, page: int | None = None, page_size: int = 100
    ) -> Table:
        """
        List organization repos.

        Pagination is supported via `page` and `page_size`.

        Args:
            organization_name: GitHub organization
            page:
                Page number to load.
                If not specified, all results are returned.
            page_size:
                Page size.
                Ignored if `page` is not set.

        """
        logger.info("Listing page %s of repos for organization %s", page, organization_name)

        return self._as_table(
            self.client.get_organization(organization_name).get_repos(),
            page=page,
            page_size=page_size,
        )

    def get_issue(self, repo_name: str, issue_number: int) -> dict[str, Any]:
        """
        Load a GitHub issue.

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
        assignee: str | Literal["none", "*"] | None = None,
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

        Pagination is supported via `page` and `page_size`.

        Args:
            repo_name: Full repo name (account/name)
            state: State of issues to return.
            assignee: Name of assigned user, "none", or "*".
            creator: Name of user that created the issue.
            mentioned: Name of user mentioned in the issue.
            labels: List of label names.
            sort: What to sort results by.
            direction: Direction to sort.
            since: Timestamp to pull issues since.
            page: Page number. All results are returned if not set.
            page_size:
                Page size.
                Ignored if `page` is not set.

        Returns:
            Repo issues

        """
        logger.info("Listing page %s of issues for repo %s", page, repo_name)

        kwargs_dict = {"state": state, "sort": sort, "direction": direction}
        if assignee:
            kwargs_dict["assignee"] = assignee
        if creator:
            kwargs_dict["creator"] = creator
        if mentioned:
            kwargs_dict["mentioned"] = mentioned
        if labels and len(labels) > 0:
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
        Load a GitHub pull request.

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
        List pull requests for a given repo.

        Pagination is supported via `page` and `page_size`.

        Args:
            repo_name: Full repo name (account/name)
            state: State of pull requests to return.
            base: Base branch to filter pull requests by.
            sort: How to sort pull requests.
            direction: Direction to sort by.
            page: Page number. All results are returned if not set.
            page_size:
                Page size.
                Ignored if `page` is not set.

        Returns:
            Repo pull requests

        """
        logger.info("Listing page %s of pull requests for repo %s", page, repo_name)

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
        List contributors for a given repo.

        Pagination is supported via `page` and `page_size`.

        Args:
            repo_name:
                Full repo name (account/name)
            page:
                Page number.
            page_size:
                Page size.
                Ignored if `page` is not set.

        Returns:
            Repo contributors

        """
        logger.info("Listing page %s of contributors for repo %s", page, repo_name)

        return self._as_table(
            self.client.get_repo(repo_name).get_contributors(),
            page=page,
            page_size=page_size,
        )

    def download_file(
        self,
        repo_name: str,
        path: str,
        branch: str | None = None,
        local_path: Path | str | None = None,
    ) -> str:
        """
        Download a file from a repo by path and branch.

        Uses the ``download_url`` directly rather than downloading via the API,
        because the API only supports downloading contents up to 1MB from a repo directly.
        The process for downloading larger files through the API is much more involved.

        Because ``download_url`` does not go through the API, it does not support username / password
        authentication and requires a token to authenticate.

        Args:
            repo_name: Full repo name (account/name)
            path: Path from the repo base directory
            branch: Branch to download file from. Defaults to repo default branch
            local_path:
                Local file path to download file to.
                Will create a temp file if not supplied.

        Returns:
            File path of downloaded file

        """
        local_path = Path(local_path or files.create_temp_file_for_path(path))

        branch = branch or self.client.get_repo(repo_name).default_branch
        logger.info("Downloading %s from %s, branch %s to %s", path, repo_name, branch, local_path)

        auth = (
            BearerAuth(req_auth.token, token_name=req_auth.token_type)
            if (req_auth := self.client.requester.auth) and (req_auth.token and req_auth.token_type)
            else None
        )
        download_url = f"https://raw.githubusercontent.com/{repo_name}/{branch}/{path}"
        res = requests.get(download_url, auth=auth)

        if res.status_code == HTTPStatus.NOT_FOUND:
            raise UnknownObjectException(status=HTTPStatus.NOT_FOUND, data=res.content)

        if res.status_code != HTTPStatus.OK:
            err_msg = f"Error downloading {path} from repo {repo_name}: {res.content}"
            raise ParsonsGitHubError(err_msg)

        local_path.write_bytes(res.content)
        logger.info("Downloaded %s to %s", path, local_path)

        return str(local_path)

    def download_table(
        self,
        repo_name: str,
        path: str,
        branch: str | None = None,
        local_path: str | None = None,
        delimiter: str = ",",
        **table_kwargs,
    ) -> Table:
        """
        Download a CSV file from a repo to a :ref:`Table` by path and branch.

        Args:
            repo_name: Full repo name (account/name)
            path: Path from the repo base directory
            branch: Branch to download file from. Defaults to repo default branch
            local_path: Local file path to download file to. Will create a temp file if not supplied.
            delimiter: The CSV delimiter to use to parse the data.
            `**table_kwargs`: Additional keyword arguments to pass to the :ref:`Table` constructor.

        """
        downloaded_file = self.download_file(repo_name, path, branch, local_path)

        return Table(petl.fromcsv(downloaded_file, delimiter=delimiter), **table_kwargs)
