import unittest

import requests_mock

from parsons import Hustle, Table
from parsons.hustle.hustle import HUSTLE_URI
from test.conftest import assert_matching_tables
from test.test_hustle import expected_json

CLIENT_ID = "FAKE_ID"
CLIENT_SECRET = "FAKE_SECRET"


class TestHustle(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m: requests_mock.Mocker):
        m.post(HUSTLE_URI + "oauth/token", json=expected_json.auth_token)
        self.hustle = Hustle(CLIENT_ID, CLIENT_SECRET)

    @requests_mock.Mocker()
    def test_auth_sets_header(self, m: requests_mock.Mocker):
        """Ensure that the Authorization header is set correctly after class initialization."""
        request_method = "GET"
        m.request(request_method, f"{HUSTLE_URI}organizations", json=expected_json.organizations)
        self.hustle._request("organizations", req_type=request_method)
        assert m.last_request is not None
        assert (
            m.last_request.headers["Authorization"]
            == f"Bearer {expected_json.auth_token['access_token']}"
        )

    @requests_mock.Mocker()
    def test_auth_header_refresh(self, m: requests_mock.Mocker):
        """Ensure that the Authorization header refreshes once the token expires."""
        # Queue a fake token that expires immediately and initialize Hustle to request it
        auth_token = {
            "access_token": "MYFAKETOKEN",
            "scope": "read:account write:account",
            "expires_in": -10,
            "token_type": "Bearer",
        }
        m.post(f"{HUSTLE_URI}oauth/token", json=auth_token)
        tmp_hustle = Hustle(CLIENT_ID, CLIENT_SECRET)

        # Queue a second fake token response without entering it into Hustle
        auth_token2 = {
            "access_token": "MYFAKETOKEN2",
            "scope": "read:account write:account",
            "expires_in": 7200,
            "token_type": "Bearer",
        }
        m.post(f"{HUSTLE_URI}oauth/token", json=auth_token2)

        # Queue a fake organizations response
        m.get(f"{HUSTLE_URI}organizations", json=expected_json.organizations)

        # Request organizations and verify the Authorization header used is the second one
        tmp_hustle._request("organizations", req_type="GET")

        assert m.last_request is not None
        assert m.last_request.headers["Authorization"] == f"Bearer {auth_token2['access_token']}"

    @requests_mock.Mocker()
    def test_get_organizations(self, m: requests_mock.Mocker):
        m.get(HUSTLE_URI + "organizations", json=expected_json.organizations)
        orgs = self.hustle.get_organizations()
        assert_matching_tables(orgs, Table(expected_json.organizations["items"]))

    @requests_mock.Mocker()
    def test_get_organization(self, m: requests_mock.Mocker):
        m.get(HUSTLE_URI + "organizations/LePEoKzD3", json=expected_json.organization)
        org = self.hustle.get_organization("LePEoKzD3")
        assert org == expected_json.organization

    @requests_mock.Mocker()
    def test_get_groups(self, m: requests_mock.Mocker):
        m.get(HUSTLE_URI + "organizations/LePEoKzD3/groups", json=expected_json.groups)
        groups = self.hustle.get_groups("LePEoKzD3")
        assert_matching_tables(groups, Table(expected_json.groups["items"]))

    @requests_mock.Mocker()
    def test_get_group(self, m: requests_mock.Mocker):
        m.get(HUSTLE_URI + "groups/zajXdqtzRt", json=expected_json.group)
        org = self.hustle.get_group("zajXdqtzRt")
        assert org == expected_json.group

    @requests_mock.Mocker()
    def test_create_lead(self, m: requests_mock.Mocker):
        m.post(HUSTLE_URI + "groups/cMCH0hxwGt/leads", json=expected_json.lead)
        lead = self.hustle.create_lead("cMCH0hxwGt", "Barack", "5126993336", last_name="Obama")
        assert lead == expected_json.lead

    @requests_mock.Mocker()
    def test_create_leads(self, m: requests_mock.Mocker):
        m.post(
            HUSTLE_URI + "groups/cMCH0hxwGt/leads",
            [
                {"json": expected_json.leads_tbl_01},
                {"json": expected_json.leads_tbl_02},
            ],
        )

        tbl = Table(
            [
                ["phone_number", "ln", "first_name"],
                ["4435705355", "Johnson", "Lyndon"],
                ["4435705354", "Richard", "Ann"],
            ]
        )
        ids = self.hustle.create_leads(tbl, group_id="cMCH0hxwGt")
        assert_matching_tables(ids, Table(expected_json.created_leads))

    @requests_mock.Mocker()
    def test_update_lead(self, m: requests_mock.Mocker):
        m.put(HUSTLE_URI + "leads/wqy78hlz2T", json=expected_json.updated_lead)
        updated_lead = self.hustle.update_lead("wqy78hlz2T", first_name="Bob")
        assert updated_lead == expected_json.updated_lead

    @requests_mock.Mocker()
    def test_get_leads(self, m: requests_mock.Mocker):
        # By Organization
        m.get(HUSTLE_URI + "organizations/cMCH0hxwGt/leads", json=expected_json.leads)
        leads = self.hustle.get_leads(organization_id="cMCH0hxwGt")
        assert_matching_tables(leads, Table(expected_json.leads["items"]))

        # By Group ID
        m.get(HUSTLE_URI + "groups/cMCH0hxwGt/leads", json=expected_json.leads)
        leads = self.hustle.get_leads(group_id="cMCH0hxwGt")
        assert_matching_tables(leads, Table(expected_json.leads["items"]))

    @requests_mock.Mocker()
    def test_get_lead(self, m: requests_mock.Mocker):
        m.get(HUSTLE_URI + "leads/wqy78hlz2T", json=expected_json.lead)
        lead = self.hustle.get_lead("wqy78hlz2T")
        assert lead == expected_json.lead

    @requests_mock.Mocker()
    def test_get_tags(self, m: requests_mock.Mocker):
        m.get(HUSTLE_URI + "organizations/LePEoKzD3/tags", json=expected_json.tags)
        tags = self.hustle.get_tags(organization_id="LePEoKzD3")
        assert_matching_tables(tags, Table(expected_json.tags["items"]))

    @requests_mock.Mocker()
    def test_get_tag(self, m: requests_mock.Mocker):
        m.get(HUSTLE_URI + "tags/zEx5rjbg5", json=expected_json.tag)
        tag = self.hustle.get_tag("zEx5rjbg5")
        assert tag == expected_json.tag

    @requests_mock.Mocker()
    def test_get_agents(self, m: requests_mock.Mocker):
        m.get(HUSTLE_URI + "groups/Qqp6o90SiE/agents", json=expected_json.agents)
        agents = self.hustle.get_agents(group_id="Qqp6o90SiE")
        assert_matching_tables(agents, Table(expected_json.agents["items"]))

    @requests_mock.Mocker()
    def test_get_agent(self, m: requests_mock.Mocker):
        m.get(HUSTLE_URI + "agents/CrJUBI1CF", json=expected_json.agent)
        agent = self.hustle.get_agent("CrJUBI1CF")
        assert agent == expected_json.agent

    @requests_mock.Mocker()
    def test_create_agent(self, m: requests_mock.Mocker):
        m.post(HUSTLE_URI + "groups/Qqp6o90Si/agents", json=expected_json.agent)
        new_agent = self.hustle.create_agent(
            "Qqp6o90Si", name="Angela", full_name="Jones", phone_number="12032498764"
        )
        assert new_agent == expected_json.agent

    @requests_mock.Mocker()
    def test_update_agent(self, m: requests_mock.Mocker):
        m.put(HUSTLE_URI + "agents/CrJUBI1CF", json=expected_json.agent)
        updated_agent = self.hustle.update_agent("CrJUBI1CF", name="Angela", full_name="Jones")
        assert updated_agent == expected_json.agent

    @requests_mock.Mocker()
    def test_create_group_membership(self, m: requests_mock.Mocker):
        m.post(HUSTLE_URI + "groups/zajXdqtzRt/memberships", json=expected_json.group)
        group_membership = self.hustle.create_group_membership("zajXdqtzRt", "A6ebDlAtqB")
        assert group_membership == expected_json.group
