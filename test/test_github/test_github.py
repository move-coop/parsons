import os
import unittest

import requests_mock

from parsons.etl.table import Table
from parsons.github.github import GitHub

_dir = os.path.dirname(__file__)


class TestGitHub(unittest.TestCase):

    def setUp(self):
        self.github = GitHub(access_token='token')

    def test_client(self):
        with self.assertRaises(KeyError):
            GitHub(None)

    @requests_mock.Mocker()
    def test_get_repo(self, m):
        with open(os.path.join(_dir, 'test_data', 'test_get_repo.json'), 'r') as f:
            m.get(requests_mock.ANY, text=f.read())
        repo = self.github.get_repo('octocat/Hello-World')
        self.assertEqual(repo['id'], 1296269)
        self.assertEqual(repo['name'], 'Hello-World')

    @requests_mock.Mocker()
    def test_list_repo_issues(self, m):
        with open(os.path.join(_dir, 'test_data', 'test_get_repo.json'), 'r') as f:
            m.get('https://api.github.com:443/repos/octocat/Hello-World', text=f.read())
        with open(os.path.join(_dir, 'test_data', 'test_list_repo_issues.json'), 'r') as f:
            m.get('https://api.github.com:443/repos/octocat/Hello-World/issues', text=f.read())
        issues_table = self.github.list_repo_issues('octocat/Hello-World')
        self.assertIsInstance(issues_table, Table)
        self.assertEqual(len(issues_table.table), 2)
        self.assertEqual(issues_table[0]['id'], 1)
        self.assertEqual(issues_table[0]['title'], 'Found a bug')

    @requests_mock.Mocker()
    def test_download_file(self, m):
        with open(os.path.join(_dir, 'test_data', 'test_get_repo.json'), 'r') as f:
            m.get('https://api.github.com:443/repos/octocat/Hello-World', text=f.read())
        with open(os.path.join(_dir, 'test_data', 'test_download_file.csv'), 'r') as f:
            m.get(
                'https://raw.githubusercontent.com/octocat/Hello-World/testing/data.csv',
                text=f.read()
            )

        file_path = self.github.download_file('octocat/Hello-World', 'data.csv', branch='testing')
        with open(file_path, 'r') as f:
            file_contents = f.read()

        self.assertEqual(file_contents, "header\ndata\n")
