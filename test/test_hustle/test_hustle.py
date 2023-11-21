import unittest
import requests_mock
from test.utils import assert_matching_tables
from test.test_hustle import expected_json
from parsons import Table, Hustle
from parsons.hustle.hustle import HUSTLE_URI

CLIENT_ID = "FAKE_ID"
CLIENT_SECRET = "FAKE_SECRET"


class TestHustle(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        m.post(HUSTLE_URI + "oauth/token", json=expected_json.auth_token)
        self.hustle = Hustle(CLIENT_ID, CLIENT_SECRET)

    @requests_mock.Mocker()
    def test_auth_token(self, m):
        self.assertEqual(
            self.hustle.auth_token, expected_json.auth_token["access_token"]
        )

    @requests_mock.Mocker()
    def test_get_organizations(self, m):
        m.get(HUSTLE_URI + "organizations", json=expected_json.organizations)
        orgs = self.hustle.get_organizations()
        assert_matching_tables(orgs, Table(expected_json.organizations["items"]))

    @requests_mock.Mocker()
    def test_get_organization(self, m):
        m.get(HUSTLE_URI + "organizations/LePEoKzD3", json=expected_json.organization)
        org = self.hustle.get_organization("LePEoKzD3")
        self.assertEqual(org, expected_json.organization)

    @requests_mock.Mocker()
    def test_get_groups(self, m):
        m.get(HUSTLE_URI + "organizations/LePEoKzD3/groups", json=expected_json.groups)
        groups = self.hustle.get_groups("LePEoKzD3")
        assert_matching_tables(groups, Table(expected_json.groups["items"]))

    @requests_mock.Mocker()
    def test_get_group(self, m):
        m.get(HUSTLE_URI + "groups/zajXdqtzRt", json=expected_json.group)
        org = self.hustle.get_group("zajXdqtzRt")
        self.assertEqual(org, expected_json.group)

    @requests_mock.Mocker()
    def test_create_lead(self, m):
        m.post(HUSTLE_URI + "groups/cMCH0hxwGt/leads", json=expected_json.lead)
        lead = self.hustle.create_lead(
            "cMCH0hxwGt", "Barack", "5126993336", last_name="Obama"
        )
        self.assertEqual(lead, expected_json.lead)

    @requests_mock.Mocker()
    def test_create_leads(self, m):
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
    def test_update_lead(self, m):
        m.put(HUSTLE_URI + "leads/wqy78hlz2T", json=expected_json.updated_lead)
        updated_lead = self.hustle.update_lead("wqy78hlz2T", first_name="Bob")
        self.assertEqual(updated_lead, expected_json.updated_lead)

    @requests_mock.Mocker()
    def test_get_leads(self, m):
        # By Organization
        m.get(HUSTLE_URI + "organizations/cMCH0hxwGt/leads", json=expected_json.leads)
        leads = self.hustle.get_leads(organization_id="cMCH0hxwGt")
        assert_matching_tables(leads, Table(expected_json.leads["items"]))

        # By Group ID
        m.get(HUSTLE_URI + "groups/cMCH0hxwGt/leads", json=expected_json.leads)
        leads = self.hustle.get_leads(group_id="cMCH0hxwGt")
        assert_matching_tables(leads, Table(expected_json.leads["items"]))

    @requests_mock.Mocker()
    def test_get_lead(self, m):
        m.get(HUSTLE_URI + "leads/wqy78hlz2T", json=expected_json.lead)
        lead = self.hustle.get_lead("wqy78hlz2T")
        self.assertEqual(lead, expected_json.lead)

    @requests_mock.Mocker()
    def test_get_tags(self, m):
        m.get(HUSTLE_URI + "organizations/LePEoKzD3/tags", json=expected_json.tags)
        tags = self.hustle.get_tags(organization_id="LePEoKzD3")
        assert_matching_tables(tags, Table(expected_json.tags["items"]))

    @requests_mock.Mocker()
    def test_get_tag(self, m):
        m.get(HUSTLE_URI + "tags/zEx5rjbg5", json=expected_json.tag)
        tag = self.hustle.get_tag("zEx5rjbg5")
        self.assertEqual(tag, expected_json.tag)

    @requests_mock.Mocker()
    def test_get_agents(self, m):
        m.get(HUSTLE_URI + "groups/Qqp6o90SiE/agents", json=expected_json.agents)
        agents = self.hustle.get_agents(group_id="Qqp6o90SiE")
        assert_matching_tables(agents, Table(expected_json.agents["items"]))

    @requests_mock.Mocker()
    def test_get_agent(self, m):
        m.get(HUSTLE_URI + "agents/CrJUBI1CF", json=expected_json.agent)
        agent = self.hustle.get_agent("CrJUBI1CF")
        self.assertEqual(agent, expected_json.agent)

    @requests_mock.Mocker()
    def test_create_agent(self, m):
        m.post(HUSTLE_URI + "groups/Qqp6o90Si/agents", json=expected_json.agent)
        new_agent = self.hustle.create_agent(
            "Qqp6o90Si", name="Angela", full_name="Jones", phone_number="12032498764"
        )
        self.assertEqual(new_agent, expected_json.agent)

    @requests_mock.Mocker()
    def test_update_agent(self, m):
        m.put(HUSTLE_URI + "agents/CrJUBI1CF", json=expected_json.agent)
        updated_agent = self.hustle.update_agent(
            "CrJUBI1CF", name="Angela", full_name="Jones"
        )
        self.assertEqual(updated_agent, expected_json.agent)

    @requests_mock.Mocker()
    def test_create_group_membership(self, m):
        m.post(HUSTLE_URI + "groups/zajXdqtzRt/memberships", json=expected_json.group)
        group_membership = self.hustle.create_group_membership(
            "zajXdqtzRt", "A6ebDlAtqB"
        )
        self.assertEqual(group_membership, expected_json.group)
