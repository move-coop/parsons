import unittest
from pathlib import Path
from unittest.mock import patch

import pytest
import requests_mock
from github.GithubException import UnknownObjectException

from parsons import GitHub, Table
from parsons.github.github import ParsonsGitHubError

_dir = Path(__file__).parent


class TestGitHub(unittest.TestCase):
    def setUp(self):
        self.github = GitHub(access_token="token")

    @requests_mock.Mocker()
    def test_wrap_github_404(self, m):
        with patch("github.Github.get_repo") as get_repo_mock:
            get_repo_mock.side_effect = UnknownObjectException("", "")
            with pytest.raises(ParsonsGitHubError):
                self.github.get_repo("octocat/Hello-World")

    @requests_mock.Mocker()
    def test_get_repo(self, m):
        m.get(requests_mock.ANY, text=(_dir / "test_data" / "test_get_repo.json").read_text())
        repo = self.github.get_repo("octocat/Hello-World")
        assert repo["id"] == 1296269
        assert repo["name"] == "Hello-World"

    @requests_mock.Mocker()
    def test_list_repo_issues(self, m):
        m.get(
            "https://api.github.com:443/repos/octocat/Hello-World",
            text=(_dir / "test_data" / "test_get_repo.json").read_text(),
        )
        m.get(
            "https://api.github.com:443/repos/octocat/Hello-World/issues",
            text=(_dir / "test_data" / "test_list_repo_issues.json").read_text(),
        )
        issues_table = self.github.list_repo_issues("octocat/Hello-World")
        assert isinstance(issues_table, Table)
        assert len(issues_table.table) == 2
        assert issues_table[0]["id"] == 1
        assert issues_table[0]["title"] == "Found a bug"

    @requests_mock.Mocker()
    def test_download_file(self, m):
        m.get(
            "https://api.github.com:443/repos/octocat/Hello-World",
            text=(_dir / "test_data" / "test_get_repo.json").read_text(),
        )
        m.get(
            "https://raw.githubusercontent.com/octocat/Hello-World/testing/data.csv",
            text=(_dir / "test_data" / "test_download_file.csv").read_text(),
        )

        file_path = self.github.download_file("octocat/Hello-World", "data.csv", branch="testing")
        file_contents = Path(file_path).read_text()

        assert file_contents == "header\ndata\n"
