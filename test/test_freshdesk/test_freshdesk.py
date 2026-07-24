"""Tests for the Freshdesk connector."""


def test_get_agents(freshdesk, requests_mock, load):
    requests_mock.get(freshdesk.uri + "agents", json=load("agents"))

    tbl = freshdesk.get_agents()

    assert tbl.num_rows == 1
    # get_agents unpacks the nested "contact" dict and drops "signature".
    assert "signature" not in tbl.columns
    assert "id" in tbl.columns


def test_get_agents_passes_filters(freshdesk, requests_mock, load):
    requests_mock.get(freshdesk.uri + "agents", json=load("agents"))

    freshdesk.get_agents(email="a@example.com", state="fulltime")

    assert requests_mock.last_request.qs["email"] == ["a@example.com"]
    assert requests_mock.last_request.qs["state"] == ["fulltime"]


def test_get_tickets(freshdesk, requests_mock, load):
    requests_mock.get(freshdesk.uri + "tickets", json=load("tickets"))

    tbl = freshdesk.get_tickets()

    assert tbl.num_rows == 1


def test_get_companies(freshdesk, requests_mock, load):
    requests_mock.get(freshdesk.uri + "companies", json=load("companies"))

    tbl = freshdesk.get_companies()

    assert tbl.num_rows == 1


def test_get_contacts(freshdesk, requests_mock, load):
    requests_mock.get(freshdesk.uri + "contacts", json=load("contacts"))

    tbl = freshdesk.get_contacts()

    assert tbl.num_rows == 1


def test_create_ticket(freshdesk, requests_mock, load):
    response = load("create_ticket_response")
    requests_mock.post(freshdesk.uri + "tickets", json=response)

    result = freshdesk.create_ticket(
        subject="Support Needed...",
        description="Details about the issue...",
        email="tom@outerspace.com",
        priority=1,
        status=2,
        cc_emails=["ram@freshdesk.com", "diana@freshdesk.com"],
    )

    assert result == response
    sent = requests_mock.last_request.json()
    assert sent["subject"] == "Support Needed..."
    assert sent["cc_emails"] == ["ram@freshdesk.com", "diana@freshdesk.com"]


def test_create_ticket_with_custom_fields(freshdesk, requests_mock, load):
    response = load("create_ticket_with_custom_fields_response")
    requests_mock.post(freshdesk.uri + "tickets", json=response)

    result = freshdesk.create_ticket(
        subject="Support Needed...",
        description="Details about the issue...",
        email="tom@outerspace.com",
        priority=1,
        status=2,
        cc_emails=["ram@freshdesk.com", "diana@freshdesk.com"],
        custom_fields={"category": "Primary"},
    )

    assert result == response
    assert requests_mock.last_request.json()["custom_fields"] == {"category": "Primary"}
