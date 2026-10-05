from http import HTTPStatus
from pathlib import Path
from unittest.mock import patch

import pytest
from github.GithubException import UnknownObjectException
from requests_mock import Mocker

from parsons import GitHub, Table
from parsons.github.github import ParsonsGitHubError

_dir = Path(__file__).parent

GITHUB_API = "https://api.github.com:443"
GITHUB_CONTENT = "https://raw.githubusercontent.com"
REPO_NAME = "octocat/Hello-World"

# TODO(eliotst): add test for get_user method
# TODO(eliotst): add test for get_organization method
# TODO(eliotst): add test for list_user_repos method
# TODO(eliotst): add test for list_organization_repos method
# TODO(eliotst): add test for get_issue method
# TODO(eliotst): add test for get_pull_request method
# TODO(eliotst): add test for list_repo_pull_requests method
# TODO(eliotst): add test for list_repo_contributors method
# TODO(eliotst): add tests for list_repo_issues arguments since, labels, mentioned, and creator


@pytest.fixture(scope="module")
def get_repo_response_text() -> str:
    """Supply test data for get_repo method."""
    return (_dir / "test_data" / "test_get_repo.json").read_text()


@pytest.fixture
def github_client() -> GitHub:
    """Initialize parsons GitHub connector for testing."""
    return GitHub()


@pytest.mark.parametrize(
    ("token", "username", "password"),
    [
        ("token", None, None),
        (None, "username", "password"),
    ],
    ids=["token", "login"],
)
def test_auth(token: str | None, username: str | None, password: str | None) -> None:
    """Ensure that the GitHub connectors is initialized with the provided credentials."""
    if token:
        github = GitHub(access_token=token)
        assert github.access_token == token
    if username and password:
        github = GitHub(username=username, password=password)
        assert github.username == username
        assert github.password == password


def test_wrap_github_404(github_client: GitHub) -> None:
    """Ensure that wrap_github_404 correctly converts a UnknownObjectException(status=404) response to a ParsonsGitHubError."""
    with patch("github.Github.get_repo") as get_repo_mock:
        get_repo_mock.side_effect = UnknownObjectException(status=HTTPStatus.NOT_FOUND)
        err_msg = "Couldn't find the object you referenced, maybe you need to log in?"
        with pytest.raises(ParsonsGitHubError, match=err_msg):
            github_client.get_repo(REPO_NAME)


def test_get_repo(
    github_client: GitHub, requests_mock: Mocker, get_repo_response_text: str
) -> None:
    """Ensure that get_repo correctly obtains repo data."""
    requests_mock.get(f"{GITHUB_API}/repos/{REPO_NAME}", text=get_repo_response_text)

    repo = github_client.get_repo(REPO_NAME)
    assert repo["id"] == 1296269
    assert repo["name"] == "Hello-World"


def test_list_repo_issues(
    github_client: GitHub, requests_mock: Mocker, get_repo_response_text: str
) -> None:
    """Ensure that list_repo_issues correctly obtains issue data."""
    repo_url = f"{GITHUB_API}/repos/{REPO_NAME}"
    requests_mock.get(repo_url, text=get_repo_response_text)
    repo_issues_data = (_dir / "test_data" / "test_list_repo_issues.json").read_text()
    requests_mock.get(f"{repo_url}/issues", text=repo_issues_data)

    issues_table = github_client.list_repo_issues(REPO_NAME)

    assert isinstance(issues_table, Table)
    assert len(issues_table.table) == 2
    assert issues_table[0]["id"] == 1
    assert issues_table[0]["title"] == "Found a bug"


def test_download_file_explicit_path(
    github_client: GitHub, requests_mock: Mocker, get_repo_response_text: str, tmp_path: Path
) -> None:
    """Ensure that download_file correctly handles an explicit local path."""
    repo_url = f"{GITHUB_API}/repos/{REPO_NAME}"
    requests_mock.get(repo_url, text=get_repo_response_text)
    downloaded_file = (_dir / "test_data" / "test_download_file.csv").read_text()
    requests_mock.get(f"{GITHUB_CONTENT}/{REPO_NAME}/master/data.csv", text=downloaded_file)

    tmp_file = tmp_path / "tmp_data.csv"
    _ = github_client.download_file(REPO_NAME, "data.csv", local_path=str(tmp_file))
    file_contents = tmp_file.read_text()

    assert file_contents == "header\ndata\n"


@pytest.mark.parametrize(
    "branch", ["main", "testing", None], ids=["main-branch", "testing-branch", "no-explicit-branch"]
)
def test_download_file_branches(
    github_client: GitHub, requests_mock: Mocker, get_repo_response_text: str, branch: str | None
) -> None:
    """Ensure that download_file correctly handles explicit / default branch."""
    test_file_text = (_dir / "test_data" / "test_download_file.csv").read_text()

    requests_mock.get(f"https://api.github.com:443/repos/{REPO_NAME}", text=get_repo_response_text)
    requests_mock.get(
        f"{GITHUB_CONTENT}/{REPO_NAME}/{branch or 'master'}/data.csv", text=test_file_text
    )

    file_path = github_client.download_file(REPO_NAME, "data.csv", branch=branch)
    file_contents = Path(file_path).read_text()

    assert file_contents == test_file_text
