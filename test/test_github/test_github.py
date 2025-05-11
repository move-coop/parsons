import unittest
from pathlib import Path
from unittest.mock import patch

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
            with self.assertRaises(ParsonsGitHubError):
                self.github.get_repo("octocat/Hello-World")

    @requests_mock.Mocker()
    def test_get_repo(self, m):
        m.get(requests_mock.ANY, text=(_dir / "test_data" / "test_get_repo.json").read_text())
        repo = self.github.get_repo("octocat/Hello-World")
        self.assertEqual(repo["id"], 1296269)
        self.assertEqual(repo["name"], "Hello-World")

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
        self.assertIsInstance(issues_table, Table)
        self.assertEqual(len(issues_table.table), 2)
        self.assertEqual(issues_table[0]["id"], 1)
        self.assertEqual(issues_table[0]["title"], "Found a bug")

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

        self.assertEqual(file_contents, "header\ndata\n")
