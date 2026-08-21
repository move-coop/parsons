"""Tests for the Action Network connector.

Action Network is an HTTP/REST API reached through ``APIConnector``, so we mock at
the HTTP layer with the ``requests_mock`` fixture and let the real connector code
(pagination, URL building, unpacking) run against it. Canned API responses live in
``data/`` and are loaded with the ``load`` fixture; the ``an`` connector and ``load``
helper are defined in conftest.py.
"""

import json

from parsons import Table
from test.conftest import assert_matching_tables

FAKE_DATE = "2019-02-29"
FAKE_PERSON_ID_1 = "action_network:fake_person_id_1"
FAKE_TAG_ID_1 = "fake_tag_id_1"
FAKE_TAG_FILTER = "name eq 'fake_tag_1'"
FAKE_FILTER_BY_EMAIL_1 = "filter eq 'fake_customer_email_1@fake_customer_email.com'"


def test_get_page(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people?page=2&per_page=2",
        text=json.dumps(load("fake_people_list_2")),
    )
    assert an._get_page("people", 2, 2) == load("fake_people_list_2")


def test_get_entry_list(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people?page=1&per_page=25",
        text=json.dumps(load("fake_people_list_1")),
    )
    requests_mock.get(
        f"{an.api_url}/people?page=2&per_page=25",
        text=json.dumps(load("fake_people_list_2")),
    )
    requests_mock.get(
        f"{an.api_url}/people?page=3&per_page=25",
        text=json.dumps({"_embedded": {"osdi:people": []}}),
    )
    assert_matching_tables(an._get_entry_list("people"), Table(load("fake_people_list")))


def test_filter_get_people(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people?page=1&per_page=25&filter={FAKE_FILTER_BY_EMAIL_1}",
        text=json.dumps(load("fake_people_list_1")),
    )
    requests_mock.get(
        f"{an.api_url}/people?page=2&per_page=25&filter={FAKE_FILTER_BY_EMAIL_1}",
        text=json.dumps(load("fake_people_list_2")),
    )
    requests_mock.get(
        f"{an.api_url}/people?page=3&per_page=25&filter={FAKE_FILTER_BY_EMAIL_1}",
        text=json.dumps({"_embedded": {"osdi:people": []}}),
    )
    assert_matching_tables(
        an.get_people(filter=FAKE_FILTER_BY_EMAIL_1),
        Table(load("fake_people_list")),
    )


def test_filter_get_entry_list(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people?page=1&per_page=25&filter={FAKE_FILTER_BY_EMAIL_1}",
        text=json.dumps(load("fake_people_list_1")),
    )
    requests_mock.get(
        f"{an.api_url}/people?page=2&per_page=25&filter={FAKE_FILTER_BY_EMAIL_1}",
        text=json.dumps(load("fake_people_list_2")),
    )
    requests_mock.get(
        f"{an.api_url}/people?page=3&per_page=25&filter={FAKE_FILTER_BY_EMAIL_1}",
        text=json.dumps({"_embedded": {"osdi:people": []}}),
    )
    assert_matching_tables(
        an._get_entry_list("people", filter=FAKE_FILTER_BY_EMAIL_1),
        Table(load("fake_people_list")),
    )


def test_filter_on_get_unsupported_entry(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/tags?page=1&per_page=25&filter={FAKE_TAG_FILTER}",
        text=json.dumps(load("fake_tag_list")),
    )
    requests_mock.get(
        f"{an.api_url}/tags?page=2&per_page=25&filter={FAKE_TAG_FILTER}",
        text=json.dumps({"_embedded": {"osdi:tags": []}}),
    )
    assert_matching_tables(
        an._get_entry_list("tags", filter=FAKE_TAG_FILTER),
        Table(load("fake_tag_list")["_embedded"]["osdi:tags"]),
    )


# Advocacy Campaigns
def test_get_advocacy_campaigns(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/advocacy_campaigns",
        text=json.dumps(load("fake_advocacy_campaigns")),
    )
    assert_matching_tables(
        an._get_entry_list("advocacy_campaigns", 1),
        load("fake_advocacy_campaigns")["_embedded"][
            list(load("fake_advocacy_campaigns")["_embedded"])[0]
        ],
    )


def test_get_advocacy_campaign(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/advocacy_campaigns/123",
        text=json.dumps(load("fake_advocacy_campaign")),
    )

    assert_matching_tables(
        an.get_advocacy_campaign("123"),
        load("fake_advocacy_campaign"),
    )


# Attendances
def test_get_person_attendances(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people/123/attendances",
        text=json.dumps(load("fake_attendances")),
    )
    assert_matching_tables(
        an.get_person_attendances("123", 1),
        load("fake_attendances")["_embedded"][list(load("fake_attendances")["_embedded"])[0]],
    )


def test_get_event_attendances(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/events/123/attendances",
        text=json.dumps(load("fake_attendances")),
    )
    assert_matching_tables(
        an.get_event_attendances("123", 1),
        load("fake_attendances")["_embedded"][list(load("fake_attendances")["_embedded"])[0]],
    )


def test_create_attendance(an, requests_mock, load):
    requests_mock.post(
        f"{an.api_url}/events/123/attendances",
        text=json.dumps(load("fake_attendance")),
    )

    assert_matching_tables(
        an.create_attendance("123", load("fake_attendance")),
        load("fake_attendance"),
    )


def test_update_attendance(an, requests_mock, load):
    requests_mock.put(
        f"{an.api_url}/events/123/attendances/123",
        text=json.dumps(load("fake_attendance")),
    )

    assert_matching_tables(
        an.update_attendance("123", "123", load("fake_attendance")),
        load("fake_attendance"),
    )


def test_get_person_attendance(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people/123/attendances/123",
        text=json.dumps(load("fake_attendance")),
    )

    assert_matching_tables(
        an.get_person_attendance("123", "123"),
        load("fake_attendance"),
    )


def test_get_event_attendance(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/events/123/attendances/123",
        text=json.dumps(load("fake_attendance")),
    )

    assert_matching_tables(
        an.get_event_attendance("123", "123"),
        load("fake_attendance"),
    )


# Campaigns
def test_get_campaigns(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/campaigns", text=json.dumps(load("fake_campaigns")))
    assert_matching_tables(
        an.get_campaigns(1),
        load("fake_campaigns")["_embedded"][list(load("fake_campaigns")["_embedded"])[0]],
    )


def test_get_campaign(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/campaigns/123",
        text=json.dumps(load("fake_campaign")),
    )

    assert_matching_tables(
        an.get_campaign("123"),
        load("fake_campaign"),
    )


# Custom Fields
def test_get_custom_fields(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/metadata/custom_fields",
        text=json.dumps(load("fake_custom_fields")),
    )

    assert_matching_tables(
        an.get_custom_fields(),
        load("fake_custom_fields"),
    )


# Donations
def test_get_donations(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/donations", text=json.dumps(load("fake_donations")))
    assert_matching_tables(
        an.get_donations(1),
        load("fake_donations")["_embedded"][list(load("fake_donations")["_embedded"])[0]],
    )


def test_get_fundraising_page_donations(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/fundraising_pages/123/donations",
        text=json.dumps(load("fake_donations")),
    )
    assert_matching_tables(
        an.get_fundraising_page_donations("123", 1),
        load("fake_donations")["_embedded"][list(load("fake_donations")["_embedded"])[0]],
    )


def test_get_person_donations(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/people/123/donations", text=json.dumps(load("fake_donations")))
    assert_matching_tables(
        an.get_person_donations("123", 1),
        load("fake_donations")["_embedded"][list(load("fake_donations")["_embedded"])[0]],
    )


def test_get_donation(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/donations/123", text=json.dumps(load("fake_donation")))
    assert_matching_tables(
        an.get_donation("123"),
        load("fake_donation"),
    )


# Embeds
def test_get_embeds(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/forms/123/embed", text=json.dumps(load("fake_embed")))
    assert_matching_tables(
        an.get_embeds("forms", "123"),
        load("fake_embed"),
    )


# Event Campaigns
def test_get_event_campaigns(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/event_campaigns",
        text=json.dumps(load("fake_event_campaigns")),
    )
    assert_matching_tables(
        an.get_event_campaigns(1),
        load("fake_event_campaigns")["_embedded"][
            list(load("fake_event_campaigns")["_embedded"])[0]
        ],
    )


def test_get_event_campaign(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/event_campaigns/123",
        text=json.dumps(load("fake_event_campaign")),
    )
    assert_matching_tables(
        an.get_event_campaign("123"),
        load("fake_event_campaign"),
    )


def test_create_event_campaign(an, requests_mock, load):
    payload = {"title": "Canvassing Events", "origin_system": "AmyforTexas.com"}
    requests_mock.post(
        f"{an.api_url}/event_campaigns", text=json.dumps(load("fake_event_campaign"))
    )
    assert load("fake_event_campaign") == an.create_event_campaign(payload)


def test_create_event_in_event_campaign(an, requests_mock, load):
    payload = {
        "title": "My Canvassing Event",
        "origin_system": "CanvassingEvents.com",
    }
    requests_mock.post(
        f"{an.api_url}/event_campaigns/123/events",
        text=json.dumps(load("fake_event")),
    )
    assert load("fake_event").items() == an.create_event_in_event_campaign("123", payload).items()


def test_update_event_campaign(an, requests_mock, load):
    payload = {"description": "This is my new event campaign description"}
    requests_mock.put(
        f"{an.api_url}/event_campaigns/123",
        text=json.dumps(load("fake_event_campaign")),
    )
    assert load("fake_event_campaign") == an.update_event_campaign("123", payload)


# Events
def test_get_events(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/events", text=json.dumps(load("fake_events")))
    assert_matching_tables(
        an.get_events(1),
        load("fake_events")["_embedded"][list(load("fake_events")["_embedded"])[0]],
    )


def test_get_event_campaign_events(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/event_campaigns/123/events",
        text=json.dumps(load("fake_events")),
    )
    assert_matching_tables(
        an.get_event_campaign_events("123", 1),
        load("fake_events")["_embedded"][list(load("fake_events")["_embedded"])[0]],
    )


def test_get_event(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/events/123", text=json.dumps(load("fake_event2")))
    assert_matching_tables(
        an.get_event("123"),
        load("fake_event2"),
    )


def test_create_event(an, requests_mock, load):
    requests_mock.post(f"{an.api_url}/events", text=json.dumps(load("fake_event")))
    assert (
        load("fake_event").items()
        == an.create_event(
            "fake_title", start_date=FAKE_DATE, location=load("fake_location")
        ).items()
    )


# Forms
def test_get_forms(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/forms",
        text=json.dumps(load("fake_forms")),
    )
    assert_matching_tables(
        an.get_forms(1),
        load("fake_forms")["_embedded"][list(load("fake_forms")["_embedded"])[0]],
    )


def test_get_form(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/forms/123", text=json.dumps(load("fake_form")))
    assert_matching_tables(
        an.get_form("123"),
        load("fake_form"),
    )


def test_create_form(an, requests_mock, load):
    payload = {"title": "My Free Form", "origin_system": "FreeForms.com"}
    requests_mock.post(f"{an.api_url}/forms", text=json.dumps(load("fake_form")))
    assert load("fake_form").items() == an.create_form(payload).items()


# Update Form
def test_update_form(an, requests_mock, load):
    payload = {"title": "My Free Form", "origin_system": "FreeForms.com"}
    requests_mock.put(f"{an.api_url}/forms/123", text=json.dumps(load("fake_form")))
    assert load("fake_form").items() == an.update_form("123", payload).items()


# Fundraising Pages
def test_get_fundraising_pages(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/fundraising_pages",
        text=json.dumps(load("fake_fundraising_pages")),
    )
    assert_matching_tables(
        an.get_fundraising_pages(1),
        load("fake_fundraising_pages")["_embedded"][
            list(load("fake_fundraising_pages")["_embedded"])[0]
        ],
    )


def test_get_fundraising_page(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/fundraising_pages/123",
        text=json.dumps(load("fake_fundraising_page")),
    )
    assert_matching_tables(
        an.get_fundraising_page("123"),
        load("fake_fundraising_page"),
    )


def test_create_fundraising_page(an, requests_mock, load):
    payload = {
        "title": "My Free Fundraiser",
        "origin_system": "FreeFundraisers.com",
    }
    requests_mock.post(
        f"{an.api_url}/fundraising_pages",
        text=json.dumps(load("fake_fundraising_page")),
    )
    assert load("fake_fundraising_page").items() == an.create_fundraising_page(payload).items()


def test_update_fundraising_page(an, requests_mock, load):
    payload = {
        "title": "My Free Fundraiser With A New Name",
        "description": "This is my free fundraiser description",
    }
    requests_mock.put(
        f"{an.api_url}/fundraising_pages/123",
        text=json.dumps(load("fake_fundraising_page")),
    )
    assert (
        load("fake_fundraising_page").items() == an.update_fundraising_page("123", payload).items()
    )


# Items
def test_get_items(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/lists/123/items",
        text=json.dumps(load("fake_items")),
    )
    assert_matching_tables(
        an.get_items("123", 1),
        load("fake_items")["_embedded"][list(load("fake_items")["_embedded"])[0]],
    )


def test_get_item(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/lists/123/items/123", text=json.dumps(load("fake_item")))
    assert_matching_tables(
        an.get_item("123", "123"),
        load("fake_item"),
    )


# Lists
def test_get_lists(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/lists",
        text=json.dumps(load("fake_lists")),
    )
    assert_matching_tables(
        an.get_lists(1),
        load("fake_lists")["_embedded"][list(load("fake_lists")["_embedded"])[0]],
    )


def test_get_list(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/lists/123", text=json.dumps(load("fake_list")))
    assert_matching_tables(
        an.get_list("123"),
        load("fake_list"),
    )


# Messages
def test_get_messages(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/messages",
        text=json.dumps(load("fake_messages")),
    )
    assert_matching_tables(
        an.get_messages(1),
        load("fake_messages")["_embedded"][list(load("fake_messages")["_embedded"])[0]],
    )


def test_get_message(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/messages/123", text=json.dumps(load("fake_message")))
    assert_matching_tables(
        an.get_message("123"),
        load("fake_message"),
    )


def test_create_message(an, requests_mock, load):
    payload = {
        "subject": "Stop doing the bad thing",
        "body": "<p>The mayor should stop doing the bad thing.</p>",
        "from": "Progressive Action Now",
        "reply_to": "jane@progressiveactionnow.org",
        "targets": [{"href": "https://actionnetwork.org/api/v2/queries/123"}],
        "_links": {"osdi:wrapper": {"href": "https://actionnetwork.org/api/v2/wrappers/123"}},
    }
    requests_mock.post(f"{an.api_url}/messages", text=json.dumps(load("fake_message")))
    assert_matching_tables(
        an.create_message(payload),
        load("fake_message"),
    )


def test_update_message(an, requests_mock, load):
    message_id = "123"
    payload = {
        "name": "Stop doing the bad thing email send 1",
        "subject": "Please! Stop doing the bad thing",
    }
    requests_mock.put(f"{an.api_url}/messages/123", text=json.dumps(load("fake_message")))
    assert_matching_tables(
        an.update_message(message_id, payload),
        load("fake_message"),
    )


def test_schedule_message(an, requests_mock):
    message_id = "123"
    scheduled_start_date = "2015-03-14T12:00:00Z"
    requests_mock.post(
        f"{an.api_url}/messages/123/schedule/",
        text=json.dumps({"message": "Your message has been scheduled"}),
    )
    assert_matching_tables(
        an.schedule_message(message_id, scheduled_start_date),
        {"message": "Your message has been scheduled"},
    )


def test_send_message(an, requests_mock):
    message_id = "123"
    requests_mock.post(
        f"{an.api_url}/messages/123/send/",
        text=json.dumps({"message": "Your email has been sent."}),
    )
    assert_matching_tables(
        an.send_message(message_id),
        {"message": "Your email has been sent."},
    )


# Metadata
def test_get_metadata(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/metadata", text=json.dumps(load("fake_metadata")))
    assert_matching_tables(
        an.get_metadata(),
        load("fake_metadata"),
    )


# Outreaches
def test_get_advocacy_campaign_outreaches(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/advocacy_campaigns/123/outreaches",
        text=json.dumps(load("fake_outreaches")),
    )
    assert_matching_tables(
        an.get_advocacy_campaign_outreaches("123", 1),
        load("fake_outreaches")["_embedded"][list(load("fake_outreaches")["_embedded"])[0]],
    )


def test_get_person_outreaches(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people/123/outreaches",
        text=json.dumps(load("fake_outreaches")),
    )
    assert_matching_tables(
        an.get_person_outreaches("123", 1),
        load("fake_outreaches")["_embedded"][list(load("fake_outreaches")["_embedded"])[0]],
    )


def test_get_advocacy_campaign_outreach(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/advocacy_campaigns/123/outreaches/123",
        text=json.dumps(load("fake_outreach")),
    )
    assert_matching_tables(
        an.get_advocacy_campaign_outreach("123", "123"),
        load("fake_outreach"),
    )


def test_get_person_outreach(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people/123/outreaches/123",
        text=json.dumps(load("fake_outreach")),
    )
    assert_matching_tables(
        an.get_person_outreach("123", "123"),
        load("fake_outreach"),
    )


def test_create_outreach(an, requests_mock, load):
    payload = {
        "targets": [{"given_name": "Joe", "family_name": "Schmoe"}],
        "_links": {"osdi:person": {"href": "https://actionnetwork.org/api/v2/people/123"}},
    }
    id = load("fake_advocacy_campaign")["identifiers"][0].split(":")[-1]
    requests_mock.post(
        f"{an.api_url}/advocacy_campaigns/{id}/outreaches",
        text=json.dumps(load("fake_outreach")),
    )
    assert_matching_tables(
        an.create_outreach(id, payload),
        load("fake_outreach"),
    )

    def test_update_outreach(self, m):
        payload = {"subject": "Please vote no!"}
        id = load("fake_advocacy_campaign")["identifiers"][0].split(":")[-1]
        requests_mock.put(
            f"{an.api_url}/advocacy_campaigns/{id}/outreaches/123",
            text=json.dumps(load("fake_outreach")),
        )
        assert_matching_tables(
            an.update_outreach(
                load("fake_advocacy_campaign")["identifiers"][0].split(":")[-1],
                "123",
                payload,
            ),
            load("fake_outreach"),
        )


# People
def test_get_people(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people?page=1&per_page=25",
        text=json.dumps(load("fake_people_list_1")),
    )
    requests_mock.get(
        f"{an.api_url}/people?page=2&per_page=25",
        text=json.dumps(load("fake_people_list_2")),
    )
    requests_mock.get(
        f"{an.api_url}/people?page=3&per_page=25",
        text=json.dumps({"_embedded": {"osdi:people": []}}),
    )
    assert_matching_tables(an.get_people(), Table(load("fake_people_list")))


def test_get_person(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people/{FAKE_PERSON_ID_1}",
        text=json.dumps(load("fake_person")),
    )
    assert an.get_person(FAKE_PERSON_ID_1) == load("fake_person")


def test_upsert_person(an, requests_mock, load):
    requests_mock.post(f"{an.api_url}/people", text=json.dumps(load("fake_upsert_person")))
    assert an.upsert_person(**load("fake_upsert_person")) == load("fake_upsert_person")


def test_update_person(an, requests_mock, load):
    requests_mock.put(
        f"{an.api_url}/people/{FAKE_PERSON_ID_1}",
        text=json.dumps(load("updated_fake_person")),
    )
    assert an.update_person(
        FAKE_PERSON_ID_1, given_name="Flake", family_name="McFlakerson"
    ) == load("updated_fake_person")


# Petitions
def test_get_petitions(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/petitions",
        text=json.dumps(load("fake_petitions")),
    )
    assert_matching_tables(
        an.get_petitions(1),
        load("fake_petitions")["_embedded"][list(load("fake_petitions")["_embedded"])[0]],
    )


def test_get_petition(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/petitions/123", text=json.dumps(load("fake_petition")))
    assert_matching_tables(
        an.get_petition("123"),
        load("fake_petition"),
    )


# Queries
def test_create_petition(an, requests_mock, load):
    fake_petition_data = {
        "title": load("fake_petition")["title"],
        "description": load("fake_petition")["description"],
        "petition_text": load("fake_petition")["petition_text"],
        "target": load("fake_petition")["target"],
    }

    requests_mock.post(
        f"{an.api_url}/petitions",
        text=json.dumps(fake_petition_data),
    )
    response = an.create_petition(
        load("fake_petition")["title"],
        load("fake_petition")["description"],
        load("fake_petition")["petition_text"],
        load("fake_petition")["target"],
    )
    assert_matching_tables(response, fake_petition_data)


def test_update_petition(an, requests_mock, load):
    fake_petition_data = {
        "title": load("fake_petition")["title"],
        "description": load("fake_petition")["description"],
        "petition_text": load("fake_petition")["petition_text"],
        "target": load("fake_petition")["target"],
    }

    requests_mock.put(
        an.api_url + "/petitions/" + load("fake_petition")["identifiers"][0].split(":")[1],
        text=json.dumps(fake_petition_data),
    )
    response = an.update_petition(
        load("fake_petition")["identifiers"][0].split(":")[1],
        title=load("fake_petition")["title"],
        description=load("fake_petition")["description"],
        petition_text=load("fake_petition")["petition_text"],
        target=load("fake_petition")["target"],
    )
    assert_matching_tables(response, fake_petition_data)


# Queries
def test_get_queries(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/queries",
        text=json.dumps(load("fake_queries")),
    )
    assert_matching_tables(
        an.get_queries(1),
        load("fake_queries")["_embedded"][list(load("fake_queries")["_embedded"])[0]],
    )


def test_get_query(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/queries/123", text=json.dumps(load("fake_query")))
    assert_matching_tables(
        an.get_query("123"),
        load("fake_query"),
    )


# Signatures
def test_get_petition_signatures(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/petitions/123/signatures",
        text=json.dumps(load("fake_signatures")),
    )
    assert_matching_tables(
        an.get_petition_signatures("123", 1),
        load("fake_signatures")["_embedded"][list(load("fake_signatures")["_embedded"])[0]],
    )


def test_get_person_signatures(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people/123/signatures",
        text=json.dumps(load("fake_signatures")),
    )
    assert_matching_tables(
        an.get_person_signatures("123", 1),
        load("fake_signatures")["_embedded"][list(load("fake_signatures")["_embedded"])[0]],
    )


def test_get_petition_signature(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/petitions/123/signatures/123",
        text=json.dumps(load("fake_signature")),
    )
    assert_matching_tables(
        an.get_petition_signature("123", "123"),
        load("fake_signature"),
    )


def test_get_person_signature(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people/123/signatures/123",
        text=json.dumps(load("fake_signature")),
    )
    assert_matching_tables(
        an.get_person_signature("123", "123"),
        load("fake_signature"),
    )


def test_create_signature(an, requests_mock, load):
    # Define the fake signature data
    fake_signature_data = {
        "comments": load("fake_signature")["comments"],
        "_links": {
            "osdi:person": {"href": load("fake_signature")["_links"]["osdi:person"]["href"]}
        },
    }

    # Mock the POST request to Action Network's signatures endpoint
    requests_mock.post(
        f"{an.api_url}/petitions/456/signatures",
        text=json.dumps(load("fake_signature")),
    )

    # Call the method to create the signature
    created_signature = an.create_signature("456", fake_signature_data)

    # Assert that the correct data is being sent and the response is handled correctly
    assert_matching_tables(created_signature, load("fake_signature"))


def test_update_signature(an, requests_mock, load):
    # Define the fake signature data with updated comments
    updated_signature_data = {
        "comments": "Updated comments",
    }

    # Mock the PATCH request to update the signature
    requests_mock.put(
        f"{an.api_url}/petitions/456/signatures/123",
        text=json.dumps(load("fake_signature")),
    )

    # Call the method to update the signature
    updated_signature = an.update_signature("456", "123", updated_signature_data)

    # Assert that the correct data is being sent and the response is handled correctly
    assert_matching_tables(updated_signature, load("fake_signature"))


# Submissions
def test_get_form_submissions(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/forms/123/submissions",
        text=json.dumps(load("fake_submissions")),
    )
    assert_matching_tables(
        an.get_form_submissions("123", 1),
        load("fake_submissions")["_embedded"][list(load("fake_submissions")["_embedded"])[0]],
    )


def test_get_person_submissions(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people/123/submissions",
        text=json.dumps(load("fake_submissions")),
    )
    assert_matching_tables(
        an.get_person_submissions("123", 1),
        load("fake_submissions")["_embedded"][list(load("fake_submissions")["_embedded"])[0]],
    )


def test_get_form_submission(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/forms/123/submissions/123",
        text=json.dumps(load("fake_submission")),
    )
    assert_matching_tables(
        an.get_form_submission("123", "123"),
        load("fake_submission"),
    )


def test_get_person_submission(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/people/123/submissions/123",
        text=json.dumps(load("fake_submission")),
    )
    assert_matching_tables(
        an.get_person_submission("123", "123"),
        load("fake_submission"),
    )


# Submissions
def test_create_submission(an, requests_mock, load):
    requests_mock.post(
        f"{an.api_url}/forms/123/submissions",
        text=json.dumps(load("fake_submission")),
    )
    assert_matching_tables(
        an.create_submission("123", "123"),
        load("fake_submission"),
    )


def test_update_submission(an, requests_mock, load):
    requests_mock.put(
        f"{an.api_url}/forms/123/submissions/123",
        json={"identifiers": ["other-system:230125s"]},
    )
    assert_matching_tables(
        an.update_submission("123", "123", {"identifiers": ["other-system:230125s"]}),
        load("fake_submission"),
    )


# Surveys
def test_get_surveys(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/surveys?page=1&per_page=25",
        text=json.dumps(load("fake_surveys")),
    )
    requests_mock.get(
        f"{an.api_url}/surveys?page=2&per_page=25",
        text=json.dumps({"_embedded": {"action_network:surveys": []}}),
    )
    assert_matching_tables(
        an.get_surveys(),
        Table(load("fake_surveys")["_embedded"]["action_network:surveys"]),
    )


def test_get_survey(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/surveys/123", text=json.dumps(load("fake_survey")))
    assert_matching_tables(
        an.get_survey("123"),
        load("fake_survey"),
    )


def test_create_survey(an, requests_mock, load):
    requests_mock.post(f"{an.api_url}/surveys", text=json.dumps(load("fake_survey_payload")))
    assert_matching_tables(
        an.create_survey(load("fake_survey_payload")),
        load("fake_survey_payload"),
    )


def test_update_survey(an, requests_mock, load):
    requests_mock.post(f"{an.api_url}/surveys/123", text=json.dumps(load("fake_survey_payload")))
    assert_matching_tables(
        an.update_survey("123", load("fake_survey_payload")),
        load("fake_survey_payload"),
    )


# Tags
def test_get_tags(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/tags?page=1&per_page=25",
        text=json.dumps(load("fake_tag_list")),
    )
    requests_mock.get(
        f"{an.api_url}/tags?page=2&per_page=25",
        text=json.dumps({"_embedded": {"osdi:tags": []}}),
    )
    assert_matching_tables(an.get_tags(), Table(load("fake_tag_list")["_embedded"]["osdi:tags"]))


def test_get_tag(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/tags/{FAKE_TAG_ID_1}", text=json.dumps(load("fake_tag")))
    assert an.get_tag(FAKE_TAG_ID_1) == load("fake_tag")


# Taggings
def test_get_taggings(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/tags/123/taggings",
        text=json.dumps(load("fake_taggings")),
    )
    assert_matching_tables(
        an.get_taggings("123", 1),
        load("fake_taggings")["_embedded"][list(load("fake_taggings")["_embedded"])[0]],
    )


def test_get_tagging(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/tags/123/taggings/123", text=json.dumps(load("fake_tagging")))
    assert_matching_tables(
        an.get_tagging("123", "123"),
        load("fake_tagging"),
    )


def test_create_tagging(an, requests_mock, load):
    requests_mock.post(
        f"{an.api_url}/tags/123/taggings",
        json=load("fake_tagging"),
    )
    assert_matching_tables(
        an.create_tagging("123", load("fake_tagging")),
        load("fake_tagging"),
    )


def test_delete_tagging(an, requests_mock):
    requests_mock.delete(
        f"{an.api_url}/tags/123/taggings/123",
        text=json.dumps({"notice": "This tagging was successfully deleted."}),
    )
    assert_matching_tables(
        an.delete_tagging("123", "123"),
        {"notice": "This tagging was successfully deleted."},
    )


# Wrappers
def test_get_wrappers(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/wrappers",
        text=json.dumps(load("fake_wrappers")),
    )
    assert_matching_tables(
        an.get_wrappers(1),
        load("fake_wrappers")["_embedded"][list(load("fake_wrappers")["_embedded"])[0]],
    )


def test_get_wrapper(an, requests_mock, load):
    requests_mock.get(f"{an.api_url}/wrappers/123", text=json.dumps(load("fake_wrapper")))
    assert_matching_tables(
        an.get_wrapper("123"),
        load("fake_wrapper"),
    )


# Unique ID Lists
def test_get_unique_id_lists(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/unique_id_lists",
        text=json.dumps(load("fake_unique_id_lists")),
    )
    assert_matching_tables(
        an.get_unique_id_lists(1),
        load("fake_unique_id_lists")["_embedded"][
            list(load("fake_unique_id_lists")["_embedded"])[0]
        ],
    )


def test_get_unique_id_list(an, requests_mock, load):
    requests_mock.get(
        f"{an.api_url}/unique_id_lists/123",
        text=json.dumps(
            load("fake_unique_id_lists")["_embedded"][
                list(load("fake_unique_id_lists")["_embedded"])[0]
            ]
        ),
    )
    assert_matching_tables(
        an.get_unique_id_list("123"),
        load("fake_unique_id_lists")["_embedded"][
            list(load("fake_unique_id_lists")["_embedded"])[0]
        ],
    )


def test_create_unique_id_list(an, requests_mock, load):
    requests_mock.post(
        f"{an.api_url}/unique_id_lists",
        text=json.dumps(
            {
                "name": load("fake_unique_id_list")["name"],
                "count": len(load("fake_unique_id_list")["unique_ids"]),
            }
        ),
    )
    assert (
        len(load("fake_unique_id_list")["unique_ids"])
        == an.create_unique_id_list(
            load("fake_unique_id_list")["name"], load("fake_unique_id_list")["unique_ids"]
        )["count"]
    )
