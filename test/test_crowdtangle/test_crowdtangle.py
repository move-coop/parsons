import unittest

import requests_mock

from parsons import CrowdTangle, Table
from test.test_crowdtangle.leaderboard import expected_leaderboard
from test.test_crowdtangle.link_post import expected_post
from test.test_crowdtangle.post import expected_posts
from test.utils import assert_matching_tables

CT_API_KEY = "FAKE_KEY"


class TestCrowdTangle(unittest.TestCase):
    def setUp(self):
        self.ct = CrowdTangle(CT_API_KEY)

    @requests_mock.Mocker()
    def test_get_posts(self, m):
        m.get(self.ct.uri + "/posts", json=expected_posts)
        posts = self.ct.get_posts()
        exp_tbl = self.ct._unpack(Table(expected_posts["result"]["posts"]))
        assert_matching_tables(posts, exp_tbl)

    @requests_mock.Mocker()
    def test_get_leaderboard(self, m):
        m.get(self.ct.uri + "/leaderboard", json=expected_leaderboard)
        leaderboard = self.ct.get_leaderboard()
        exp_tbl = self.ct._unpack(Table(expected_leaderboard["result"]["accountStatistics"]))
        assert_matching_tables(leaderboard, exp_tbl)

    @requests_mock.Mocker()
    def test_get_links(self, m):
        m.get(self.ct.uri + "/links", json=expected_post)
        post = self.ct.get_links(link="https://nbcnews.to/34stfC2")
        exp_tbl = self.ct._unpack(Table(expected_post["result"]["posts"]))
        assert_matching_tables(post, exp_tbl)
