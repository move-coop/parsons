"""Tests for the Hustle connector."""

from parsons import Table
from parsons.hustle.hustle import HUSTLE_URI
from test.conftest import assert_matching_tables


def test_auth_token(hustle, load):
    assert hustle.auth_token == load("auth_token")["access_token"]


def test_get_organizations(hustle, requests_mock, load):
    organizations = load("organizations")
    requests_mock.get(HUSTLE_URI + "organizations", json=organizations)

    orgs = hustle.get_organizations()

    assert_matching_tables(orgs, Table(organizations["items"]))


def test_get_organization(hustle, requests_mock, load):
    organization = load("organization")
    requests_mock.get(HUSTLE_URI + "organizations/LePEoKzD3", json=organization)

    assert hustle.get_organization("LePEoKzD3") == organization


def test_get_groups(hustle, requests_mock, load):
    groups = load("groups")
    requests_mock.get(HUSTLE_URI + "organizations/LePEoKzD3/groups", json=groups)

    assert_matching_tables(hustle.get_groups("LePEoKzD3"), Table(groups["items"]))


def test_get_group(hustle, requests_mock, load):
    group = load("group")
    requests_mock.get(HUSTLE_URI + "groups/zajXdqtzRt", json=group)

    assert hustle.get_group("zajXdqtzRt") == group


def test_create_lead(hustle, requests_mock, load):
    lead = load("lead")
    requests_mock.post(HUSTLE_URI + "groups/cMCH0hxwGt/leads", json=lead)

    result = hustle.create_lead("cMCH0hxwGt", "Barack", "5126993336", last_name="Obama")

    assert result == lead


def test_create_leads(hustle, requests_mock, load):
    requests_mock.post(
        HUSTLE_URI + "groups/cMCH0hxwGt/leads",
        [{"json": load("leads_tbl_01")}, {"json": load("leads_tbl_02")}],
    )

    tbl = Table(
        [
            ["phone_number", "ln", "first_name"],
            ["4435705355", "Johnson", "Lyndon"],
            ["4435705354", "Richard", "Ann"],
        ]
    )
    ids = hustle.create_leads(tbl, group_id="cMCH0hxwGt")

    assert_matching_tables(ids, Table(load("created_leads")))


def test_update_lead(hustle, requests_mock, load):
    updated_lead = load("updated_lead")
    requests_mock.put(HUSTLE_URI + "leads/wqy78hlz2T", json=updated_lead)

    assert hustle.update_lead("wqy78hlz2T", first_name="Bob") == updated_lead


def test_get_leads_by_organization(hustle, requests_mock, load):
    leads = load("leads")
    requests_mock.get(HUSTLE_URI + "organizations/cMCH0hxwGt/leads", json=leads)

    assert_matching_tables(hustle.get_leads(organization_id="cMCH0hxwGt"), Table(leads["items"]))


def test_get_leads_by_group(hustle, requests_mock, load):
    leads = load("leads")
    requests_mock.get(HUSTLE_URI + "groups/cMCH0hxwGt/leads", json=leads)

    assert_matching_tables(hustle.get_leads(group_id="cMCH0hxwGt"), Table(leads["items"]))


def test_get_lead(hustle, requests_mock, load):
    lead = load("lead")
    requests_mock.get(HUSTLE_URI + "leads/wqy78hlz2T", json=lead)

    assert hustle.get_lead("wqy78hlz2T") == lead


def test_get_tags(hustle, requests_mock, load):
    tags = load("tags")
    requests_mock.get(HUSTLE_URI + "organizations/LePEoKzD3/tags", json=tags)

    assert_matching_tables(hustle.get_tags(organization_id="LePEoKzD3"), Table(tags["items"]))


def test_get_tag(hustle, requests_mock, load):
    tag = load("tag")
    requests_mock.get(HUSTLE_URI + "tags/zEx5rjbg5", json=tag)

    assert hustle.get_tag("zEx5rjbg5") == tag


def test_get_agents(hustle, requests_mock, load):
    agents = load("agents")
    requests_mock.get(HUSTLE_URI + "groups/Qqp6o90SiE/agents", json=agents)

    assert_matching_tables(hustle.get_agents(group_id="Qqp6o90SiE"), Table(agents["items"]))


def test_get_agent(hustle, requests_mock, load):
    agent = load("agent")
    requests_mock.get(HUSTLE_URI + "agents/CrJUBI1CF", json=agent)

    assert hustle.get_agent("CrJUBI1CF") == agent


def test_create_agent(hustle, requests_mock, load):
    agent = load("agent")
    requests_mock.post(HUSTLE_URI + "groups/Qqp6o90Si/agents", json=agent)

    result = hustle.create_agent(
        "Qqp6o90Si", name="Angela", full_name="Jones", phone_number="12032498764"
    )

    assert result == agent
    assert requests_mock.last_request.json()["name"] == "Angela"


def test_update_agent(hustle, requests_mock, load):
    agent = load("agent")
    requests_mock.put(HUSTLE_URI + "agents/CrJUBI1CF", json=agent)

    assert hustle.update_agent("CrJUBI1CF", name="Angela", full_name="Jones") == agent


def test_create_group_membership(hustle, requests_mock, load):
    group = load("group")
    requests_mock.post(HUSTLE_URI + "groups/zajXdqtzRt/memberships", json=group)

    assert hustle.create_group_membership("zajXdqtzRt", "A6ebDlAtqB") == group


def test_create_custom_field(hustle, requests_mock):
    requests_mock.post(HUSTLE_URI + "organizations/LePEoKzD3/custom-fields", json={"ok": True})

    hustle.create_custom_field("LePEoKzD3", name="Region")

    assert requests_mock.last_request.json() == {"name": "Region"}


def test_create_custom_field_with_agent_visibility(hustle, requests_mock):
    """agent_visible is only added to the payload when it is explicitly set."""
    requests_mock.post(HUSTLE_URI + "organizations/LePEoKzD3/custom-fields", json={"ok": True})

    hustle.create_custom_field("LePEoKzD3", name="Region", agent_visible=False)

    assert requests_mock.last_request.json() == {"name": "Region", "agentVisible": False}
