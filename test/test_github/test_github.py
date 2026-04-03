from pathlib import Path
from unittest.mock import patch

import pytest
from github.GithubException import UnknownObjectException

from parsons import GitHub, Table
from parsons.github.github import ParsonsGitHubError

_dir = Path(__file__).parent


@pytest.fixture(scope="module")
def get_repo_response_text() -> str:
    return (_dir / "test_data" / "test_get_repo.json").read_text()


@pytest.fixture
def github_client() -> GitHub:
    return GitHub(access_token="token")


def test_wrap_github_404(github_client):
    with patch("github.Github.get_repo") as get_repo_mock:
        get_repo_mock.side_effect = UnknownObjectException(404)
        with pytest.raises(ParsonsGitHubError):
            github_client.get_repo("octocat/Hello-World")


def test_get_repo(github_client, requests_mock, get_repo_response_text):
    requests_mock.get(
        "https://api.github.com:443/repos/octocat/Hello-World",
        text=get_repo_response_text,
    )

    repo = github_client.get_repo("octocat/Hello-World")
    assert repo["id"] == 1296269
    assert repo["name"] == "Hello-World"


def test_list_repo_issues(github_client, requests_mock, get_repo_response_text):
    requests_mock.get(
        "https://api.github.com:443/repos/octocat/Hello-World",
        text=get_repo_response_text,
    )
    requests_mock.get(
        "https://api.github.com:443/repos/octocat/Hello-World/issues",
        text=(_dir / "test_data" / "test_list_repo_issues.json").read_text(),
    )

    issues_table = github_client.list_repo_issues("octocat/Hello-World")

    assert isinstance(issues_table, Table)
    assert len(issues_table.table) == 2
    assert issues_table[0]["id"] == 1
    assert issues_table[0]["title"] == "Found a bug"


def test_download_file(github_client, requests_mock, get_repo_response_text):
    requests_mock.get(
        "https://api.github.com:443/repos/octocat/Hello-World",
        text=get_repo_response_text,
    )
    requests_mock.get(
        "https://raw.githubusercontent.com/octocat/Hello-World/testing/data.csv",
        text=(_dir / "test_data" / "test_download_file.csv").read_text(),
    )

    file_path = github_client.download_file("octocat/Hello-World", "data.csv", branch="testing")
    file_contents = Path(file_path).read_text()

    assert file_contents == "header\ndata\n"
