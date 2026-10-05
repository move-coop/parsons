from http import HTTPStatus
from pathlib import Path
from unittest.mock import patch

import petl
import pytest
from github.GithubException import UnknownObjectException
from requests_mock import Mocker

from parsons import GitHub, Table
from parsons.github.github import ParsonsGitHubError
from test.conftest import assert_matching_tables

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
        assert github.client.requester.auth
        assert github.client.requester.auth.token == token
    if username and password:
        github = GitHub(username=username, password=password)
        assert github.client.requester.auth
        assert github.client.requester.auth.login == username
        assert github.client.requester.auth.password == password


def test_auth_token_in_header(requests_mock: Mocker, get_repo_response_text: str) -> None:
    """Ensure that get_repo correctly obtains repo data."""
    requests_mock.get(f"{GITHUB_API}/repos/{REPO_NAME}", text=get_repo_response_text)

    github_client = GitHub(access_token="test_auth_token")
    github_client.get_repo(REPO_NAME)

    assert (request := requests_mock.last_request)
    assert "Authorization" in request.headers
    assert github_client.client.requester.auth
    auth_token_type = github_client.client.requester.auth.token_type
    auth_token = github_client.client.requester.auth.token
    assert request.headers["Authorization"] == f"{auth_token_type} {auth_token}"


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


@pytest.mark.parametrize(
    ("status_code", "err_msg"),
    [
        (HTTPStatus.OK, None),
        (
            HTTPStatus.NOT_FOUND,
            "Couldn't find the object you referenced, maybe you need to log in?",
        ),
        (HTTPStatus.ACCEPTED, f"Error downloading data.csv from repo {REPO_NAME}"),
        (HTTPStatus.INTERNAL_SERVER_ERROR, f"Error downloading data.csv from repo {REPO_NAME}"),
    ],
    ids=["200", "404", "202", "500"],
)
@pytest.mark.parametrize(
    "branch", ["main", "testing", None], ids=["main-branch", "testing-branch", "no-explicit-branch"]
)
@pytest.mark.parametrize("path_type", [str, Path, None], ids=["string", "Path", "none"])
def test_download_file(
    github_client: GitHub,
    requests_mock: Mocker,
    get_repo_response_text: str,
    tmp_path: Path,
    branch: str | None,
    path_type: type,
    status_code: int,
    err_msg: str | None,
) -> None:
    """Ensure that download_file works correctly in various configurations."""
    repo_url = f"{GITHUB_API}/repos/{REPO_NAME}"
    requests_mock.get(repo_url, text=get_repo_response_text)
    downloaded_file = (_dir / "test_data" / "test_download_file.csv").read_text()
    requests_mock.get(
        f"{GITHUB_CONTENT}/{REPO_NAME}/{branch or 'master'}/data.csv",
        status_code=status_code,
        text=downloaded_file,
    )

    tmp_file = path_type(tmp_path / "tmp_data.csv") if path_type else None
    if err_msg is not None:
        with pytest.raises(ParsonsGitHubError, match=err_msg):
            _ = github_client.download_file(
                REPO_NAME, "data.csv", local_path=tmp_file, branch=branch
            )
    else:
        tmp_file = github_client.download_file(
            REPO_NAME, "data.csv", local_path=tmp_file, branch=branch
        )
        assert Path(tmp_file).read_text() == "header\ndata\n"


def test_download_table(
    github_client: GitHub,
    requests_mock: Mocker,
    get_repo_response_text: str,
) -> None:
    """Ensure that download_table correctly downlods as CSV to a Table object."""
    repo_url = f"{GITHUB_API}/repos/{REPO_NAME}"
    requests_mock.get(repo_url, text=get_repo_response_text)
    csv_file = _dir / "test_data" / "test_download_file.csv"
    requests_mock.get(f"{GITHUB_CONTENT}/{REPO_NAME}/master/data.csv", text=csv_file.read_text())

    downloaded_tbl = github_client.download_table(REPO_NAME, "data.csv")

    expected_tbl = Table(petl.fromcsv(csv_file))

    assert_matching_tables(downloaded_tbl, expected_tbl)
