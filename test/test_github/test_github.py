import os
import unittest
from unittest.mock import patch

import requests_mock
from github.GithubException import UnknownObjectException

from parsons import GitHub, Table
from parsons.github.github import ParsonsGitHubError

_dir = os.path.dirname(__file__)


class TestGitHub(unittest.TestCase):
    def setUp(self):
        self.github = GitHub(access_token="token")

    @requests_mock.Mocker()
    def test_wrap_github_404(self, m):
        with patch("github.Github.get_repo") as get_repo_mock:
            get_repo_mock.side_effect = UnknownObjectException("", "")
            with self.assertRaises(ParsonsGitHubError):
                self.github.get_repo("octocat/Hello-World")

    @requests_mock.Mocker()
    def test_get_repo(self, m):
        with open(os.path.join(_dir, "test_data", "test_get_repo.json"), "r") as f:
            m.get(requests_mock.ANY, text=f.read())
        repo = self.github.get_repo("octocat/Hello-World")
        assert repo["id"] == 1296269
        assert repo["name"] == "Hello-World"

    @requests_mock.Mocker()
    def test_list_repo_issues(self, m):
        with open(os.path.join(_dir, "test_data", "test_get_repo.json"), "r") as f:
            m.get("https://api.github.com:443/repos/octocat/Hello-World", text=f.read())
        with open(os.path.join(_dir, "test_data", "test_list_repo_issues.json"), "r") as f:
            m.get(
                "https://api.github.com:443/repos/octocat/Hello-World/issues",
                text=f.read(),
            )
        issues_table = self.github.list_repo_issues("octocat/Hello-World")
        assert isinstance(issues_table, Table)
        assert len(issues_table.table) == 2
        assert issues_table[0]["id"] == 1
        assert issues_table[0]["title"] == "Found a bug"

    @requests_mock.Mocker()
    def test_download_file(self, m):
        with open(os.path.join(_dir, "test_data", "test_get_repo.json"), "r") as f:
            m.get("https://api.github.com:443/repos/octocat/Hello-World", text=f.read())
        with open(os.path.join(_dir, "test_data", "test_download_file.csv"), "r") as f:
            m.get(
                "https://raw.githubusercontent.com/octocat/Hello-World/testing/data.csv",
                text=f.read(),
            )

        file_path = self.github.download_file("octocat/Hello-World", "data.csv", branch="testing")
        with open(file_path, "r") as f:
            file_contents = f.read()

        assert file_contents == "header\ndata\n"
