"""Tests for the CrowdTangle connector."""

from parsons import Table
from test.conftest import assert_matching_tables


def test_get_posts(crowdtangle, requests_mock, load):
    posts_response = load("posts")
    requests_mock.get(crowdtangle.uri + "/posts", json=posts_response)

    posts = crowdtangle.get_posts()

    expected = crowdtangle._unpack(Table(posts_response["result"]["posts"]))
    assert_matching_tables(posts, expected)
    assert posts.num_rows == len(posts_response["result"]["posts"])


def test_get_leaderboard(crowdtangle, requests_mock, load):
    leaderboard_response = load("leaderboard")
    requests_mock.get(crowdtangle.uri + "/leaderboard", json=leaderboard_response)

    leaderboard = crowdtangle.get_leaderboard()

    expected = crowdtangle._unpack(Table(leaderboard_response["result"]["accountStatistics"]))
    assert_matching_tables(leaderboard, expected)
    assert leaderboard.num_rows == len(leaderboard_response["result"]["accountStatistics"])


def test_get_links(crowdtangle, requests_mock, load):
    links_response = load("links")
    requests_mock.get(crowdtangle.uri + "/links", json=links_response)

    posts = crowdtangle.get_links(link="https://nbcnews.to/34stfC2")

    expected = crowdtangle._unpack(Table(links_response["result"]["posts"]))
    assert_matching_tables(posts, expected)
    assert requests_mock.last_request.qs["link"] == ["https://nbcnews.to/34stfc2"]
