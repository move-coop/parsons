import logging

import requests
from github import Github as PyGithub

from parsons.etl.table import Table
from parsons.utilities import check_env, files

logger = logging.getLogger(__name__)


class GitHub(object):
    """Creates a GitHub class for accessing the GitHub API.

    Uses ``parsons.utilities.check_env`` to load credentials from environment variables if not
    supplied, and requires either an access token or a username and password.

    Args:
        username: Optional[str]
            Username of account to use for credentials. Can be set with ``GITHUB_USERNAME``
            environment variable.
        password: Optional[str]
            Password of account to use for credentials. Can be set with ``GITHUB_PASSWORD``
            environment variable.
        access_token: Optional[str]
            Access token to use for credentials. Can be set with ``GITHUB_ACCESS_TOKEN`` environment
            variable.
    """

    def __init__(self, username=None, password=None, access_token=None):

        self.username = check_env.check('GITHUB_USERNAME', username, optional=True)
        self.password = check_env.check('GITHUB_PASSWORD', password, optional=True)
        self.access_token = check_env.check('GITHUB_ACCESS_TOKEN', access_token, optional=True)

        if self.username and self.password:
            self.client = PyGithub(self.username, self.password)
        elif self.access_token:
            self.client = PyGithub(self.access_token)
        else:
            raise KeyError(
                'username, password or access_token must be supplied to use the GitHub connector'
            )

    def _as_table(self, paginated_list, page, page_size):
        """Converts a single page in a paginated list into a Parsons ``Table``. Uses the
        ``_rawData`` property of each item instead of calling ``raw_data`` to avoid making a
        separate request for each item in a page for types that PyGithub doesn't consider complete.

        Args:
            paginated_list: ``pygithub.PaginatedList.PaginatedList``
                PyGithub paginated list
            page: int
                Page number to load
            page_size: int
                Page size

        Returns:
            ``Table``
                Table object created from the raw data of the list
        """

        page_start = (page - 1) * page_size
        page_end = page_start + page_size

        return Table([
            list_item._rawData
            for list_item
            in paginated_list[page_start:page_end]]
        )

    def get_user(self, username):
        """Loads a GitHub user by username

        Args:
            username: str
                Username of user to load

        Returns:
            dict
                User information
        """

        return self.client.get_user(username).raw_data

    def get_organization(self, organization_name):
        """Loads a GitHub organization by name

        Args:
            organization_name: str
                Name of organization to load

        Returns:
            dict
                Organization information
        """

        return self.client.get_organization(organization_name).raw_data

    def get_repo(self, repo_name):
        """Loads a GitHub repo by name

        Args:
            repo_name: str
                Full repo name (account/name)

        Returns:
            dict
                Repo information
        """

        return self.client.get_repo(repo_name).raw_data

    def list_user_repos(self, username, page=1, page_size=25):
        """List user repos with pagination, returning a ``Table``

        Args:
            username: str
                GitHub username
            page: int
                Page number. Defaults to 1
            page_size: int
                Page size. Defaults to 25.

        Returns:
            ``Table``
                Table with page of user repos
        """

        logger.info(f'Listing page {page} of repos for user {username}')

        return self._as_table(self.client.get_user(username).get_repos(), page, page_size)

    def list_organization_repos(self, organization_name, page=1, page_size=25):
        """List organization repos with pagination, returning a ``Table``

        Args:
            organization_name: str
                GitHub organization name
            page: int
                Page number. Defaults to 1.
            page_size: int
                Page size. Defaults to 25.

        Returns:
            ``Table``
                Table with page of organization repos
        """

        logger.info(f'Listing page {page} of repos for organization {organization_name}')

        return self._as_table(
            self.client.get_organization(organization_name).get_repos(), page, page_size
        )

    def get_issue(self, repo_name, issue_number):
        """Loads a GitHub issue

        Args:
            repo_name: str
                Full repo name (account/name)
            issue_number: int
                Number of issue to load

        Returns:
            dict
                Issue information
        """

        return self.client.get_repo(repo_name).get_issue(number=issue_number).raw_data

    def list_repo_issues(self, repo_name, state="open", assignee=None, creator=None, mentioned=None,
                         labels=[], sort="created", direction="desc", since=None, page=1,
                         page_size=25):
        """List issues for a given repo

        Args:
            repo_name: str
                Full repo name (account/name)
            state: str
                State of issues to return. One of "open", "closed", "all". Defaults to "open".
            assignee: Optional[str]
                Name of assigned user, "none", or "*".
            creator: Optional[str]
                Name of user that created the issue.
            mentioned: Optional[str]
                Name of user mentioned in the issue.
            labels: list[str]
                List of label names. Defaults to []
            sort: str
                What to sort results by. One of "created", "updated", "comments". Defaults to
                "created".
            direction: str
                Direction to sort. One of "asc", "desc". Defaults to "desc".
            since: Optional[Union[datetime.datetime, datetime.date]]
                Timestamp to pull issues since. Defaults to None.
            page: int
                Page number. Defaults to 1.
            page_size: int
                Page size. Defaults to 25.

        Returns:
            ``Table``
                Table with page of repo issues
        """

        logger.info(f'Listing page {page} of issues for repo {repo_name}')

        kwargs_dict = {"state": state, "sort": sort, "direction": direction}
        if assignee:
            kwargs_dict["assignee"] = assignee
        if creator:
            kwargs_dict["creator"] = creator
        if mentioned:
            kwargs_dict["mentioned"] = mentioned
        if len(labels) > 0:
            kwargs_dict["labels"] = ",".join(labels)
        if since:
            kwargs_dict["since"] = f'{since.isoformat()[:19]}Z'

        return self._as_table(
            self.client.get_repo(repo_name).get_issues(**kwargs_dict), page, page_size
        )

    def get_pull_request(self, repo_name, pull_request_number):
        """Loads a GitHub pull request

        Args:
            repo_name: str
                Full repo name (account/name)
            pull_request_number: int
                Pull request number

        Returns:
            dict
                Pull request information
        """

        return self.client.get_repo(repo_name).get_pull(pull_request_number).raw_data

    def list_repo_pull_requests(self, repo_name, state="open", base=None, sort="created",
                                direction="desc", page=1, page_size=25):
        """Lists pull requests for a given repo

        Args:
            repo_name: str
                Full repo name (account/name)
            state: str
                One of "open, "closed", "all". Defaults to "open".
            base: Optional[str]
                Base branch to filter pull requests by.
            sort: str
                How to sort pull requests. One of "created", "updated", "popularity". Defaults to
                "created".
            direction: str
                Direction to sort by. Defaults to "desc".
            page: int
                Page number. Defaults to 1.
            page_size: int
                Page size. Defaults to 25.

        Returns:
            ``Table``
                Table with page of repo pull requests
        """

        logger.info(f'Listing page {page} of pull requests for repo {repo_name}')

        kwargs_dict = {"state": state, "sort": sort, "direction": direction}
        if base:
            kwargs_dict["base"] = base

        self._as_table(self.client.get_repo(repo_name).get_pulls(**kwargs_dict), page, page_size)

    def list_repo_contributors(self, repo_name, page=1, page_size=25):
        """Lists contributors for a given repo

        Args:
            repo_name: str
                Full repo name (account/name)
            page: int
                Page number. Defaults to 1.
            page_size: int
                Page size. Defaults to 25.

        Returns:
            ``Table``
                Table with page of repo contributors
        """

        logger.info(f'Listing page {page} of contributors for repo {repo_name}')

        return self._as_table(self.client.get_repo(repo_name).get_contributors(), page, page_size)

    def download_file(self, repo_name, path, branch=None, local_path=None):
        """Download a file from a repo by path and branch. Defaults to the repo's default branch if
        branch is not supplied.

        Uses the download_url directly rather than the API because the API only supports contents up
        to 1MB from a repo directly, and the process for downloading larger files through the API is
        much more involved.

        Args:
            repo_name: str
                Full repo name (account/name)
            path: str
                Path from the repo base directory
            branch: Optional[str]
                Branch to download file from. Defaults to repo default branch
            local_path: Optional[str]
                Local file path to download file to. Will create a temp file if not supplied.

        Returns:
            str
                File path of downloaded file
        """

        if not local_path:
            local_path = files.create_temp_file_for_path('TEMPFILEGITHUB')

        repo = self.client.get_repo(repo_name)
        if branch is None:
            branch = repo.default_branch

        logger.info(f'Downloading {path} from {repo_name}, branch {branch} to {local_path}')

        res = requests.get(f'https://raw.githubusercontent.com/{repo_name}/{branch}/{path}')
        with open(local_path, 'wb') as f:
            f.write(res.content)

        logger.info(f'Downloaded {path} to {local_path}')

        return local_path
