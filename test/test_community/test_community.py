"""Tests for the Community connector."""

from parsons import Community
from parsons.community.community import COMMUNITY_API_ENDPOINT

FILENAME = "campaigns"
EXPORT_CSV = b'"CAMPAIGN_ID","LEADER_ID"\n"0288","6e83b"\n'


def test_uri_falls_back_to_default_endpoint(monkeypatch, client_id, client_token):
    """With no URL supplied or in the environment, the client id builds the URI."""
    monkeypatch.delenv("COMMUNITY_URL", raising=False)

    com = Community(client_id, client_token)

    assert com.uri == f"{COMMUNITY_API_ENDPOINT}/{client_id}/"


def test_get_request_uses_segment_path_for_subscription_export(community, uri, requests_mock):
    """`outbound_message_type_usage` is fetched from a different path than every other export."""
    filename = "outbound_message_type_usage"
    requests_mock.get(f"{uri}/{filename}.csv.gz/segment-based-subscription", content=EXPORT_CSV)

    assert community.get_request(filename=filename) == EXPORT_CSV


def test_get_request(community, uri, requests_mock):
    requests_mock.get(f"{uri}/{FILENAME}.csv.gz", content=EXPORT_CSV)

    assert community.get_request(filename=FILENAME) == EXPORT_CSV


def test_get_request_sends_bearer_token(community, uri, requests_mock):
    requests_mock.get(f"{uri}/{FILENAME}.csv.gz", content=EXPORT_CSV)

    community.get_request(filename=FILENAME)

    assert requests_mock.last_request.headers["Authorization"] == "Bearer somesecret"


def test_get_data_export(community, uri, requests_mock):
    requests_mock.get(f"{uri}/{FILENAME}.csv.gz", content=EXPORT_CSV)

    tbl = community.get_data_export(FILENAME)

    assert tbl.columns == ["CAMPAIGN_ID", "LEADER_ID"]
    assert tbl.num_rows == 1
    assert tbl[0]["CAMPAIGN_ID"] == "0288"
    assert tbl[0]["LEADER_ID"] == "6e83b"
