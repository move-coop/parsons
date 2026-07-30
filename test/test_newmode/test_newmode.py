from unittest.mock import call

import pytest
from oauthlib.oauth2 import TokenExpiredError
from requests.exceptions import HTTPError

from parsons import Table
from test.conftest import assert_matching_tables
from test.test_newmode import test_newmode_data

V2_API_URL = "https://base.newmode.net/api/"
V2_API_AUTH_URL = "https://base.newmode.net/oauth/token/"
V2_API_CAMPAIGNS_URL = "https://base.newmode.net/"


# ---------------------------------------------------------------------------
# V1: wraps the third-party ``Newmode`` client (mocked at that SDK boundary).
# ---------------------------------------------------------------------------


def test_get_tools(newmode_v1):
    args = {}
    response = newmode_v1.get_tools(args)
    newmode_v1.client.getTools.assert_called_with(params=args)
    assert response[0]["title"] == "Tool 1"


def test_get_tool(newmode_v1):
    id = 1
    response = newmode_v1.get_tool(id)
    newmode_v1.client.getTool.assert_called_with(id, params={})
    assert response["name"] == "Tool 1"


def test_lookup_targets(newmode_v1):
    id = 1
    response = newmode_v1.lookup_targets(id)
    newmode_v1.client.lookupTargets.assert_called_with(id, None, params={})
    assert response[0]["full_name"] == "John Doe"


def test_get_action(newmode_v1):
    id = 1
    response = newmode_v1.get_action(id)
    newmode_v1.client.getAction.assert_called_with(id, params={})
    assert response["required_fields"][0]["key"] == "first_name"


def test_run_action(newmode_v1):
    id = 1
    payload = {
        "email": "john.doe@example.com",
        "first_name": "John",
    }
    response = newmode_v1.run_action(id, payload)
    newmode_v1.client.runAction.assert_called_with(id, payload, params={})
    assert response == 1


def test_get_target(newmode_v1):
    id = "TESTMODE-aasfff"
    response = newmode_v1.get_target(id)
    newmode_v1.client.getTarget.assert_called_with(id, params={})
    assert response["id"] == 1
    assert response["full_name"] == "John Doe"


def test_get_campaigns(newmode_v1):
    args = {}
    response = newmode_v1.get_campaigns(args)
    newmode_v1.client.getCampaigns.assert_called_with(params=args)
    assert response[0]["title"] == "Campaign 1"


def test_get_campaign(newmode_v1):
    id = 1
    response = newmode_v1.get_campaign(id)
    newmode_v1.client.getCampaign.assert_called_with(id, params={})
    assert response["name"] == "Campaign 1"


def test_get_organizations(newmode_v1):
    args = {}
    response = newmode_v1.get_organizations(args)
    newmode_v1.client.getOrganizations.assert_called_with(params=args)
    assert response[0]["title"] == "Organization 1"


def test_get_organization(newmode_v1):
    id = 1
    response = newmode_v1.get_organization(id)
    newmode_v1.client.getOrganization.assert_called_with(id, params={})
    assert response["name"] == "Organization 1"


def test_get_services(newmode_v1):
    args = {}
    response = newmode_v1.get_services(args)
    newmode_v1.client.getServices.assert_called_with(params=args)
    assert response[0]["title"] == "Service 1"


def test_get_service(newmode_v1):
    id = 1
    response = newmode_v1.get_service(id)
    newmode_v1.client.getService.assert_called_with(id, params={})
    assert response["name"] == "Service 1"


def test_get_outreaches(newmode_v1):
    id = 1
    args = {}
    response = newmode_v1.get_outreaches(id, args)
    newmode_v1.client.getOutreaches.assert_called_with(id, params=args)
    assert response[0]["title"] == "Outreach 1"


def test_get_outreach(newmode_v1):
    id = 1
    response = newmode_v1.get_outreach(id)
    newmode_v1.client.getOutreach.assert_called_with(id, params={})
    assert response["name"] == "Outreach 1"


def test_get_tools_empty_response(newmode_v1):
    newmode_v1.client.getTools.return_value = []
    args = {}
    response = newmode_v1.get_tools(args)
    newmode_v1.client.getTools.assert_called_with(params=args)
    assert response.num_rows == 0


def test_get_tool_invalid_id(newmode_v1):
    err = "Invalid ID"
    newmode_v1.client.getTool.side_effect = HTTPError(err)
    with pytest.raises(HTTPError, match=err):
        newmode_v1.get_tool(-1)


def test_get_campaigns_pagination(newmode_v1):
    newmode_v1.client.getCampaigns.side_effect = [
        [{"id": 1, "title": "Campaign 1"}],
        [{"id": 2, "title": "Campaign 2"}],
        [],
    ]
    args = {"page": 1}
    all_campaigns = []
    while True:
        response = newmode_v1.get_campaigns(args)
        all_campaigns.extend(response)
        if not response:
            break
        args["page"] += 1
    assert len(all_campaigns) == 2
    assert all_campaigns[0]["title"] == "Campaign 1"
    assert all_campaigns[1]["title"] == "Campaign 2"


# ---------------------------------------------------------------------------
# V2: uses APIConnector/requests (mocked at the HTTP boundary).
# ---------------------------------------------------------------------------


def test_get_campaign_v2(newmode_v2, requests_mock):
    json_response = test_newmode_data.get_campaign_json_response
    tbl = Table([json_response])
    requests_mock.get(
        f"{newmode_v2.base_url}/campaign/{newmode_v2.campaign_id}/form",
        json=json_response,
    )
    assert_matching_tables(newmode_v2.get_campaign(campaign_id=newmode_v2.campaign_id), tbl)


def test_get_campaign_ids(newmode_v2, requests_mock):
    lst = ["testCampaingID"]
    json_response = test_newmode_data.get_campaign_ids_json_response
    requests_mock.get(f"{V2_API_CAMPAIGNS_URL}jsonapi/node/action", json=json_response)
    assert_matching_tables(newmode_v2.get_campaign_ids(), lst)


def test_get_recipient(newmode_v2, requests_mock):
    city = "Vancouver"
    json_response = test_newmode_data.get_recipient_json_response

    tbl = Table([json_response])
    requests_mock.get(
        f"{newmode_v2.base_url}/campaign/{newmode_v2.campaign_id}/target", json=json_response
    )
    assert_matching_tables(
        newmode_v2.get_recipient(campaign_id=newmode_v2.campaign_id, city=city), tbl
    )


def test_run_submit(newmode_v2, requests_mock):
    json_response = test_newmode_data.run_submit_json_response
    json_input = {
        "action_id": newmode_v2.campaign_id,
        "first_name": "TestFirstName",
        "last_name": "TestLastName",
        "email": "test_abc@test.com",
        "opt_in": 1,
        "address": {"postal_code": "V6A 2T2"},
        "subject": "This is my subject",
        "message": "This is my letter",
    }

    requests_mock.post(
        f"{newmode_v2.base_url}/campaign/{newmode_v2.campaign_id}/submit",
        json=json_response,
    )
    assert_matching_tables(
        newmode_v2.run_submit(campaign_id=newmode_v2.campaign_id, json=json_input),
        json_response,
    )


def test_base_request_retries(newmode_v2, requests_mock, mocker):
    mock_logger = mocker.patch("parsons.newmode.newmode.logger")
    requests_mock.get(
        f"{V2_API_URL}v2.1/test-endpoint",
        status_code=500,
    )

    with pytest.raises(HTTPError, match=f"Code: 500; URL: {V2_API_URL}v2.1/test-endpoint"):
        newmode_v2.base_request(
            method="GET",
            url=f"{V2_API_URL}v2.1/test-endpoint",
            retries=2,
        )

    # Verify that the logger warned about retries
    assert mock_logger.warning.call_count == 2
    mock_logger.warning.assert_has_calls(
        [
            call("Request failed (attempt 1/2). Retrying..."),
            call("Request failed (attempt 2/2). Retrying..."),
        ]
    )
    # Verify that the logger logged an error after retries failed
    mock_logger.error.assert_called_once_with("Request failed after 2 retries.")


def test_get_campaign_empty_response(newmode_v2, requests_mock):
    requests_mock.get(f"{newmode_v2.base_url}/campaign/{newmode_v2.campaign_id}/form", json=[])
    response = newmode_v2.get_campaign(campaign_id=newmode_v2.campaign_id)
    assert response.num_rows == 0


def test_checked_response_success(newmode_v2, requests_mock):
    response_data = {"key": "value"}
    requests_mock.get(f"{V2_API_URL}v2.1/test-endpoint", json=response_data, status_code=200)

    response = newmode_v2.default_client.request(
        url=f"{V2_API_URL}v2.1/test-endpoint", req_type="GET"
    )
    result = newmode_v2.checked_response(response, newmode_v2.default_client)
    assert result == response_data


def test_checked_response_invalid_json(newmode_v2, requests_mock):
    requests_mock.get(f"{V2_API_URL}v2.1/test-endpoint", text="Invalid JSON", status_code=200)

    response = newmode_v2.default_client.request(
        url=f"{V2_API_URL}v2.1/test-endpoint", req_type="GET"
    )
    with pytest.raises(ValueError, match="API request encountered an error"):
        newmode_v2.checked_response(response, newmode_v2.default_client)


def test_checked_response_http_error(newmode_v2, requests_mock):
    requests_mock.get(f"{V2_API_URL}v2.1/test-endpoint", status_code=404)

    response = newmode_v2.default_client.request(
        url=f"{V2_API_URL}v2.1/test-endpoint", req_type="GET", raise_on_error=False
    )
    with pytest.raises(
        HTTPError, match=f"404 Client Error: None for url: {V2_API_URL}v2.1/test-endpoint"
    ):
        newmode_v2.checked_response(response, newmode_v2.default_client)


def test_token_refresh_on_expired_token(newmode_v2, requests_mock, mocker):
    mock_get_default_oauth_client = mocker.patch(
        "parsons.newmode.newmode.NewmodeV2.get_default_oauth_client"
    )

    mock_new_client = mocker.MagicMock()
    mock_get_default_oauth_client.return_value = mock_new_client

    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "success"}
    mock_new_client.request.return_value = mock_response

    mock_new_client.json_check.return_value = True

    call_state = {"count": 0}

    def oauth_side_effect(*args, **kwargs):
        if call_state["count"] == 0:
            call_state["count"] += 1
            raise TokenExpiredError()
        return mock_response

    mocker.patch.object(newmode_v2.default_client, "request", side_effect=oauth_side_effect)
    requests_mock.get(f"{V2_API_URL}v2.1/test-endpoint", json={"data": "success"}, status_code=200)
    response = newmode_v2.base_request(method="GET", url=f"{V2_API_URL}v2.1/test-endpoint")

    mock_get_default_oauth_client.assert_called_once()
    assert response == {"data": "success"}
    mock_new_client.request.assert_called_with(
        url=f"{V2_API_URL}v2.1/test-endpoint", req_type="GET", json=None, data=None, params={}
    )
