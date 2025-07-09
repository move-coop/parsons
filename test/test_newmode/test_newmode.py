import os
import unittest
import unittest.mock as mock
from unittest.mock import call, patch

import requests_mock
from oauthlib.oauth2 import TokenExpiredError
from requests.exceptions import HTTPError

from parsons import Newmode, Table
from test.test_newmode import test_newmode_data
from test.utils import assert_matching_tables

CLIENT_ID = "fakeClientID"
CLIENT_SECRET = "fakeClientSecret"


V2_API_URL = "https://base.newmode.net/api/"
V2_API_AUTH_URL = "https://base.newmode.net/oauth/token/"
V2_API_CAMPAIGNS_URL = "https://base.newmode.net/"


class TestNewmodeV1(unittest.TestCase):
    def setUp(self):
        os.environ["NEWMODE_API_USER"] = "MYFAKEUSERNAME"
        os.environ["NEWMODE_API_PASSWORD"] = "MYFAKEPASSWORD"

        self.nm = Newmode()
        self.nm.client = mock.MagicMock()

        self.nm.client.getTools.return_value = [
            {"id": 1, "title": "Tool 1"},
            {"id": 2, "title": "Tool 2"},
        ]

        self.nm.client.getTool.return_value = {"id": 1, "name": "Tool 1"}

        self.nm.client.getAction.return_value = {
            "required_fields": [
                {
                    "key": "first_name",
                    "name": "First Name",
                    "type": "textfield",
                    "value": "",
                }
            ]
        }

        self.nm.client.lookupTargets.return_value = {
            "0": {"unique_id": "TESTMODE-uniqueid", "full_name": "John Doe"}
        }

        self.nm.client.runAction.return_value = {"sid": 1}

        self.nm.client.getTarget.return_value = {"id": 1, "full_name": "John Doe"}

        self.nm.client.getCampaigns.return_value = [
            {"id": 1, "title": "Campaign 1"},
            {"id": 2, "title": "Campaign 2"},
        ]

        self.nm.client.getCampaign.return_value = {"id": 1, "name": "Campaign 1"}

        self.nm.client.getOrganizations.return_value = [
            {"id": 1, "title": "Organization 1"},
            {"id": 2, "title": "Organization 2"},
        ]

        self.nm.client.getOrganization.return_value = {
            "id": 1,
            "name": "Organization 1",
        }

        self.nm.client.getServices.return_value = [
            {"id": 1, "title": "Service 1"},
            {"id": 2, "title": "Service 2"},
        ]

        self.nm.client.getService.return_value = {"id": 1, "name": "Service 1"}

        self.nm.client.getOutreaches.return_value = [
            {"id": 1, "title": "Outreach 1"},
            {"id": 2, "title": "Outreach 2"},
        ]

        self.nm.client.getOutreach.return_value = {"id": 1, "name": "Outreach 1"}

    def test_get_tools(self):
        args = {}
        response = self.nm.get_tools(args)
        self.nm.client.getTools.assert_called_with(params=args)
        self.assertEqual(response[0]["title"], "Tool 1")

    def test_get_tool(self):
        id = 1
        response = self.nm.get_tool(id)
        self.nm.client.getTool.assert_called_with(id, params={})
        self.assertEqual(response["name"], "Tool 1")

    def test_lookup_targets(self):
        id = 1
        response = self.nm.lookup_targets(id)
        self.nm.client.lookupTargets.assert_called_with(id, None, params={})
        self.assertEqual(response[0]["full_name"], "John Doe")

    def test_get_action(self):
        id = 1
        response = self.nm.get_action(id)
        self.nm.client.getAction.assert_called_with(id, params={})
        self.assertEqual(response["required_fields"][0]["key"], "first_name")

    def test_run_action(self):
        id = 1
        payload = {
            "email": "john.doe@example.com",
            "first_name": "John",
        }
        response = self.nm.run_action(id, payload)
        self.nm.client.runAction.assert_called_with(id, payload, params={})
        self.assertEqual(response, 1)

    def test_get_target(self):
        id = "TESTMODE-aasfff"
        response = self.nm.get_target(id)
        self.nm.client.getTarget.assert_called_with(id, params={})
        self.assertEqual(response["id"], 1)
        self.assertEqual(response["full_name"], "John Doe")

    def test_get_campaigns(self):
        args = {}
        response = self.nm.get_campaigns(args)
        self.nm.client.getCampaigns.assert_called_with(params=args)
        self.assertEqual(response[0]["title"], "Campaign 1")

    def test_get_campaign(self):
        id = 1
        response = self.nm.get_campaign(id)
        self.nm.client.getCampaign.assert_called_with(id, params={})
        self.assertEqual(response["name"], "Campaign 1")

    def test_get_organizations(self):
        args = {}
        response = self.nm.get_organizations(args)
        self.nm.client.getOrganizations.assert_called_with(params=args)
        self.assertEqual(response[0]["title"], "Organization 1")

    def test_get_organization(self):
        id = 1
        response = self.nm.get_organization(id)
        self.nm.client.getOrganization.assert_called_with(id, params={})
        self.assertEqual(response["name"], "Organization 1")

    def test_get_services(self):
        args = {}
        response = self.nm.get_services(args)
        self.nm.client.getServices.assert_called_with(params=args)
        self.assertEqual(response[0]["title"], "Service 1")

    def test_get_service(self):
        id = 1
        response = self.nm.get_service(id)
        self.nm.client.getService.assert_called_with(id, params={})
        self.assertEqual(response["name"], "Service 1")

    def test_get_outreaches(self):
        id = 1
        args = {}
        response = self.nm.get_outreaches(id, args)
        self.nm.client.getOutreaches.assert_called_with(id, params=args)
        self.assertEqual(response[0]["title"], "Outreach 1")

    def test_get_outreach(self):
        id = 1
        response = self.nm.get_outreach(id)
        self.nm.client.getOutreach.assert_called_with(id, params={})
        self.assertEqual(response["name"], "Outreach 1")

    def test_get_tools_empty_response(self):
        self.nm.client.getTools.return_value = []
        args = {}
        response = self.nm.get_tools(args)
        self.nm.client.getTools.assert_called_with(params=args)
        self.assertEqual(response.num_rows, 0)

    def test_get_tool_invalid_id(self):
        self.nm.client.getTool.side_effect = HTTPError("Invalid ID")
        with self.assertRaises(HTTPError):
            self.nm.get_tool(-1)

    def test_get_campaigns_pagination(self):
        self.nm.client.getCampaigns.side_effect = [
            [{"id": 1, "title": "Campaign 1"}],
            [{"id": 2, "title": "Campaign 2"}],
            [],
        ]
        args = {"page": 1}
        all_campaigns = []
        while True:
            response = self.nm.get_campaigns(args)
            all_campaigns.extend(response)
            if not response:
                break
            args["page"] += 1
        self.assertEqual(len(all_campaigns), 2)
        self.assertEqual(all_campaigns[0]["title"], "Campaign 1")
        self.assertEqual(all_campaigns[1]["title"], "Campaign 2")


class TestNewmodeV2(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        m.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        api_version = "v2.1"
        self.nm = Newmode(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, api_version=api_version)
        self.campaign_id = "fakeCampaignID"
        self.base_url = f"{V2_API_URL}{api_version}"

    @requests_mock.Mocker()
    def test_get_campaign(self, m):
        json_response = test_newmode_data.get_campaign_json_response
        tbl = Table([json_response])
        m.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(
            f"{self.base_url}/campaign/{self.campaign_id}/form",
            json=json_response,
        )
        assert_matching_tables(self.nm.get_campaign(campaign_id=self.campaign_id), tbl)

    @requests_mock.Mocker()
    def test_get_campaign_ids(self, m):
        lst = ["testCampaingID"]
        json_response = test_newmode_data.get_campaign_ids_json_response
        m.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(f"{V2_API_CAMPAIGNS_URL}jsonapi/node/action", json=json_response)
        assert_matching_tables(self.nm.get_campaign_ids(), lst)

    @requests_mock.Mocker()
    def test_get_recipient(self, m):
        self.city = "Vancouver"
        json_response = test_newmode_data.get_recipient_json_response

        tbl = Table([json_response])
        m.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(f"{self.base_url}/campaign/{self.campaign_id}/target", json=json_response)
        assert_matching_tables(
            self.nm.get_recipient(campaign_id=self.campaign_id, city=self.city), tbl
        )

    @requests_mock.Mocker()
    def test_run_submit(self, m):
        json_response = test_newmode_data.run_submit_json_response
        json_input = {
            "action_id": self.campaign_id,
            "first_name": "TestFirstName",
            "last_name": "TestLastName",
            "email": "test_abc@test.com",
            "opt_in": 1,
            "address": {"postal_code": "V6A 2T2"},
            "subject": "This is my subject",
            "message": "This is my letter",
        }

        m.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.post(
            f"{self.base_url}/campaign/{self.campaign_id}/submit",
            json=json_response,
        )
        assert_matching_tables(
            self.nm.run_submit(campaign_id=self.campaign_id, json=json_input),
            json_response,
        )

    @requests_mock.Mocker()
    @patch("parsons.newmode.newmode.logger")
    def test_base_request_retries(self, m, mock_logger):
        m.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(
            f"{V2_API_URL}v2.1/test-endpoint",
            status_code=500,
        )

        with self.assertRaises(HTTPError):
            self.nm.base_request(
                method="GET",
                url=f"{V2_API_URL}v2.1/test-endpoint",
                retries=2,
            )

        # Verify that the logger warned about retries
        self.assertEqual(mock_logger.warning.call_count, 2)
        mock_logger.warning.assert_has_calls(
            [
                call("Request failed (attempt 1/2). Retrying..."),
                call("Request failed (attempt 2/2). Retrying..."),
            ]
        )
        # Verify that the logger logged an error after retries failed
        mock_logger.error.assert_called_once_with("Request failed after 2 retries.")

    @requests_mock.Mocker()
    def test_get_campaign_empty_response(self, m):
        m.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(f"{self.base_url}/campaign/{self.campaign_id}/form", json=[])
        response = self.nm.get_campaign(campaign_id=self.campaign_id)
        self.assertEqual(response.num_rows, 0)

    @requests_mock.Mocker()
    def test_checked_response_success(self, m):
        m.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        response_data = {"key": "value"}
        m.get(f"{V2_API_URL}v2.1/test-endpoint", json=response_data, status_code=200)

        response = self.nm.default_client.request(
            url=f"{V2_API_URL}v2.1/test-endpoint", req_type="GET"
        )
        result = self.nm.checked_response(response, self.nm.default_client)
        self.assertEqual(result, response_data)

    @requests_mock.Mocker()
    def test_checked_response_invalid_json(self, m):
        m.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(f"{V2_API_URL}v2.1/test-endpoint", text="Invalid JSON", status_code=200)

        response = self.nm.default_client.request(
            url=f"{V2_API_URL}v2.1/test-endpoint", req_type="GET"
        )
        with self.assertRaises(ValueError):
            self.nm.checked_response(response, self.nm.default_client)

    @requests_mock.Mocker()
    def test_checked_response_http_error(self, m):
        m.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(f"{V2_API_URL}v2.1/test-endpoint", status_code=404)

        response = self.nm.default_client.request(
            url=f"{V2_API_URL}v2.1/test-endpoint", req_type="GET"
        )
        with self.assertRaises(HTTPError):
            self.nm.checked_response(response, self.nm.default_client)

    @requests_mock.Mocker()
    @patch("parsons.newmode.newmode.NewmodeV2.get_default_oauth_client")
    def test_token_refresh_on_expired_token(self, m, mock_get_default_oauth_client):
        m.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})

        # Mock the new client returned by get_default_oauth_client
        mock_new_client = mock.MagicMock()
        mock_get_default_oauth_client.return_value = mock_new_client

        # Configure the mock response for the request
        mock_response = mock.MagicMock()
        mock_response.raise_for_status = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}

        # Simulate token expiration and successful response
        def oauth_side_effect(*args, **kwargs):
            if not hasattr(self, "call_count"):
                self.call_count = 0
            if self.call_count == 0:
                self.call_count += 1
                raise TokenExpiredError()
            return mock_response

        with patch.object(self.nm.default_client, "request", side_effect=oauth_side_effect):
            m.get(f"{V2_API_URL}v2.1/test-endpoint", json={"data": "success"}, status_code=200)
            response = self.nm.base_request(method="GET", url=f"{V2_API_URL}v2.1/test-endpoint")

        mock_get_default_oauth_client.assert_called_once()
        self.assertEqual(response, {"data": "success"})
        mock_new_client.request.assert_called_with(
            url=f"{V2_API_URL}v2.1/test-endpoint", req_type="GET", json=None, data=None, params={}
        )
