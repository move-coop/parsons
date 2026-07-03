import pytest

from parsons import Newmode

CLIENT_ID = "fakeClientID"
CLIENT_SECRET = "fakeClientSecret"

V2_API_URL = "https://base.newmode.net/api/"
V2_API_AUTH_URL = "https://base.newmode.net/oauth/token/"
V2_API_CAMPAIGNS_URL = "https://base.newmode.net/"


@pytest.fixture
def newmode_v1(monkeypatch, mocker):
    """
    Build a NewmodeV1 connector whose underlying third-party ``Newmode`` client
    is swapped out for a MagicMock, and pre-wire canned return values.
    """
    monkeypatch.setenv("NEWMODE_API_USER", "MYFAKEUSERNAME")
    monkeypatch.setenv("NEWMODE_API_PASSWORD", "MYFAKEPASSWORD")

    nm = Newmode()
    nm.client = mocker.MagicMock()

    nm.client.getTools.return_value = [
        {"id": 1, "title": "Tool 1"},
        {"id": 2, "title": "Tool 2"},
    ]

    nm.client.getTool.return_value = {"id": 1, "name": "Tool 1"}

    nm.client.getAction.return_value = {
        "required_fields": [
            {
                "key": "first_name",
                "name": "First Name",
                "type": "textfield",
                "value": "",
            }
        ]
    }

    nm.client.lookupTargets.return_value = {
        "0": {"unique_id": "TESTMODE-uniqueid", "full_name": "John Doe"}
    }

    nm.client.runAction.return_value = {"sid": 1}

    nm.client.getTarget.return_value = {"id": 1, "full_name": "John Doe"}

    nm.client.getCampaigns.return_value = [
        {"id": 1, "title": "Campaign 1"},
        {"id": 2, "title": "Campaign 2"},
    ]

    nm.client.getCampaign.return_value = {"id": 1, "name": "Campaign 1"}

    nm.client.getOrganizations.return_value = [
        {"id": 1, "title": "Organization 1"},
        {"id": 2, "title": "Organization 2"},
    ]

    nm.client.getOrganization.return_value = {
        "id": 1,
        "name": "Organization 1",
    }

    nm.client.getServices.return_value = [
        {"id": 1, "title": "Service 1"},
        {"id": 2, "title": "Service 2"},
    ]

    nm.client.getService.return_value = {"id": 1, "name": "Service 1"}

    nm.client.getOutreaches.return_value = [
        {"id": 1, "title": "Outreach 1"},
        {"id": 2, "title": "Outreach 2"},
    ]

    nm.client.getOutreach.return_value = {"id": 1, "name": "Outreach 1"}

    return nm


@pytest.fixture
def newmode_v2(requests_mock):
    """
    Build a NewmodeV2 connector, mocking the OAuth token POST so the two
    OAuth2APIConnector clients can be constructed without hitting the network.
    """
    requests_mock.post(V2_API_AUTH_URL, json={"access_token": "fakeAccessToken"})
    api_version = "v2.1"
    nm = Newmode(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, api_version=api_version)
    nm.campaign_id = "fakeCampaignID"
    nm.base_url = f"{V2_API_URL}{api_version}"
    return nm
