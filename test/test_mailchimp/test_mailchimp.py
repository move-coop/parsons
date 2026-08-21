"""Tests for the Mailchimp connector."""


def test_get_campaigns(mailchimp, requests_mock, load):
    requests_mock.get(mailchimp.uri + "campaigns", json=load("campaigns"))

    tbl = mailchimp.get_campaigns()

    assert tbl.num_rows == 2


def test_get_campaigns_passes_query_params(mailchimp, requests_mock, load):
    requests_mock.get(mailchimp.uri + "campaigns", json=load("campaigns"))

    mailchimp.get_campaigns(count=5, sort_field="create_time", sort_dir="DESC")

    qs = requests_mock.last_request.qs
    assert qs["count"] == ["5"]
    assert qs["sort_field"] == ["create_time"]
    assert qs["sort_dir"] == ["desc"]


def test_get_lists(mailchimp, requests_mock, load):
    requests_mock.get(mailchimp.uri + "lists", json=load("lists"))

    tbl = mailchimp.get_lists()

    assert tbl.num_rows == 2


def test_get_members(mailchimp, requests_mock, load):
    requests_mock.get(mailchimp.uri + "lists/zyx/members", json=load("members"))

    tbl = mailchimp.get_members(list_id="zyx")

    assert tbl.num_rows == 2


def test_get_unsubscribes(mailchimp, requests_mock, load):
    requests_mock.get(mailchimp.uri + "reports/abc/unsubscribed", json=load("unsubscribes"))

    tbl = mailchimp.get_unsubscribes(campaign_id="abc")

    assert tbl.num_rows == 1
