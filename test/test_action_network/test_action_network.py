import json
from typing import Literal

import pytest
from requests_mock import Mocker

from parsons import ActionNetwork, Table
from test.conftest import assert_matching_tables
from test.test_action_network.conftest import API_URL


@pytest.mark.parametrize("request_type", ["GET", "POST", "PUT", "DELETE"])
def test_request_auth_header(
    requests_mock: Mocker,
    an: ActionNetwork,
    request_type: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
) -> None:
    requests_mock.request(request_type, API_URL)

    res = an.api.request(API_URL, request_type)

    assert an.api_token
    assert "OSDI-API-Token" in res.request.headers
    assert res.request.headers["OSDI-API-Token"] == an.api_token


def test_get_page(requests_mock: Mocker, an: ActionNetwork, fake_people_list_2: dict) -> None:
    req_url = f"{API_URL}/people?page=2&per_page=2"
    requests_mock.get(req_url, text=json.dumps(fake_people_list_2))

    res_json = an._get_page("people", 2, 2)

    assert isinstance(res_json, dict)
    assert res_json == fake_people_list_2


def test_get_page_per_page_limit(
    requests_mock: Mocker, an: ActionNetwork, fake_people_list_2: dict
) -> None:
    """Ensure that per_page values over 25 are reduced to 25."""
    req_url = f"{API_URL}/people?page=2&per_page=25"
    req = requests_mock.get(req_url, text=json.dumps(fake_people_list_2))

    _ = an._get_page("people", 2, 30)

    assert req.last_request
    assert req.last_request.url == f"{API_URL}/people?page=2&per_page=25"


def test_get_entry_list(
    requests_mock: Mocker,
    an: ActionNetwork,
    fake_people_list_1: dict,
    fake_people_list_2: dict,
    fake_people_list: list[dict],
) -> None:
    pages = (fake_people_list_1, fake_people_list_2, {"_embedded": {"osdi:people": []}})
    for pg_no, pg_data in enumerate(pages):
        req_url = f"{API_URL}/people?page={pg_no + 1}&per_page=25"
        requests_mock.get(req_url, text=json.dumps(pg_data))

    res_json = an._get_entry_list("people")

    assert isinstance(res_json, Table)
    assert_matching_tables(res_json, Table(fake_people_list))


def test_filter_get_entry_list(
    requests_mock: Mocker,
    an: ActionNetwork,
    fake_filter_by_email_1: str,
    fake_people_list_1: dict,
    fake_people_list_2: dict,
    fake_people_list: list[dict],
) -> None:
    pages = (fake_people_list_1, fake_people_list_2, {"_embedded": {"osdi:people": []}})
    for pg_no, pg_data in enumerate(pages):
        req_url = f"{API_URL}/people?page={pg_no + 1}&per_page=25&filter={fake_filter_by_email_1}"
        requests_mock.get(req_url, text=json.dumps(pg_data))

    res_json = an._get_entry_list("people", filter=fake_filter_by_email_1)

    assert isinstance(res_json, Table)
    assert_matching_tables(res_json, Table(fake_people_list))


def test_filter_on_get_unsupported_entry(
    requests_mock: Mocker, an: ActionNetwork, fake_tag_filter: str, fake_tag_list: dict
) -> None:
    pages = (fake_tag_list, {"_embedded": {"osdi:people": []}})
    for pg_no, pg_data in enumerate(pages):
        req_url = f"{API_URL}/tags?page={pg_no + 1}&per_page=25&filter={fake_tag_filter}"
        requests_mock.get(req_url, text=json.dumps(pg_data))

    res_json = an._get_entry_list("tags", filter=fake_tag_filter)

    assert isinstance(res_json, Table)
    assert_matching_tables(res_json, Table(fake_tag_list["_embedded"]["osdi:tags"]))


class TestAdvocacyCampaigns:
    def test_get_advocacy_campaigns(
        self, requests_mock: Mocker, an: ActionNetwork, fake_advocacy_campaigns: dict
    ) -> None:
        req_url = f"{API_URL}/advocacy_campaigns"
        requests_mock.get(req_url, text=json.dumps(fake_advocacy_campaigns))

        res_json = an._get_entry_list("advocacy_campaigns", 1)

        assert isinstance(res_json, Table)
        embedded = fake_advocacy_campaigns["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_advocacy_campaign(
        self, requests_mock: Mocker, an: ActionNetwork, fake_advocacy_campaign: dict
    ) -> None:
        req_url = f"{API_URL}/advocacy_campaigns/123"
        requests_mock.get(req_url, text=json.dumps(fake_advocacy_campaign))

        res_json = an.get_advocacy_campaign("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_advocacy_campaign)


class TestAttendances:
    def test_get_person_attendances(
        self, requests_mock: Mocker, an: ActionNetwork, fake_attendances: dict
    ) -> None:
        req_url = f"{API_URL}/people/123/attendances"
        requests_mock.get(req_url, text=json.dumps(fake_attendances))

        res_json = an.get_person_attendances("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_attendances["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_event_attendances(
        self, requests_mock: Mocker, an: ActionNetwork, fake_attendances: dict
    ) -> None:
        req_url = f"{API_URL}/events/123/attendances"
        requests_mock.get(req_url, text=json.dumps(fake_attendances))

        res_json = an.get_event_attendances("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_attendances["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_create_attendance(
        self, requests_mock: Mocker, an: ActionNetwork, fake_attendance: dict
    ) -> None:
        req_url = f"{API_URL}/events/123/attendances"
        requests_mock.post(req_url, text=json.dumps(fake_attendance))

        res_json = an.create_attendance("123", fake_attendance)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_attendance)

    def test_update_attendance(
        self, requests_mock: Mocker, an: ActionNetwork, fake_attendance: dict
    ) -> None:
        req_url = f"{API_URL}/events/123/attendances/123"
        requests_mock.put(req_url, text=json.dumps(fake_attendance))

        res_json = an.update_attendance("123", "123", fake_attendance)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_attendance)

    def test_get_person_attendance(
        self, requests_mock: Mocker, an: ActionNetwork, fake_attendance: dict
    ) -> None:
        req_url = f"{API_URL}/people/123/attendances/123"
        requests_mock.get(req_url, text=json.dumps(fake_attendance))

        res_json = an.get_person_attendance("123", "123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_attendance)

    def test_get_event_attendance(
        self, requests_mock: Mocker, an: ActionNetwork, fake_attendance: dict
    ) -> None:
        req_url = f"{API_URL}/events/123/attendances/123"
        requests_mock.get(req_url, text=json.dumps(fake_attendance))

        res_json = an.get_event_attendance("123", "123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_attendance)


class TestCampaigns:
    def test_get_campaigns(
        self, requests_mock: Mocker, an: ActionNetwork, fake_campaigns: dict
    ) -> None:
        req_url = f"{API_URL}/campaigns"
        requests_mock.get(req_url, text=json.dumps(fake_campaigns))

        res_json = an.get_campaigns(1)

        assert isinstance(res_json, Table)
        embedded = fake_campaigns["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_campaign(
        self, requests_mock: Mocker, an: ActionNetwork, fake_campaign: dict
    ) -> None:
        req_url = f"{API_URL}/campaigns/123"
        requests_mock.get(req_url, text=json.dumps(fake_campaign))

        res_json = an.get_campaign("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_campaign)


class TestCustomFields:
    def test_get_custom_fields(
        self, requests_mock: Mocker, an: ActionNetwork, fake_custom_fields: dict
    ) -> None:
        req_url = f"{API_URL}/metadata/custom_fields"
        requests_mock.get(req_url, text=json.dumps(fake_custom_fields))

        assert_matching_tables(an.get_custom_fields(), fake_custom_fields)


class TestDonations:
    def test_get_donations(
        self, requests_mock: Mocker, an: ActionNetwork, fake_donations: dict
    ) -> None:
        req_url = f"{API_URL}/donations"
        requests_mock.get(req_url, text=json.dumps(fake_donations))

        res_json = an.get_donations(1)

        assert isinstance(res_json, Table)
        embedded = fake_donations["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_fundraising_page_donations(
        self, requests_mock: Mocker, an: ActionNetwork, fake_donations: dict
    ) -> None:
        req_url = f"{API_URL}/fundraising_pages/123/donations"
        requests_mock.get(req_url, text=json.dumps(fake_donations))

        res_json = an.get_fundraising_page_donations("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_donations["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_person_donations(
        self, requests_mock: Mocker, an: ActionNetwork, fake_donations: dict
    ) -> None:
        req_url = f"{API_URL}/people/123/donations"
        requests_mock.get(req_url, text=json.dumps(fake_donations))

        res_json = an.get_person_donations("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_donations["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_donation(
        self, requests_mock: Mocker, an: ActionNetwork, fake_donation: dict
    ) -> None:
        req_url = f"{API_URL}/donations/123"
        requests_mock.get(req_url, text=json.dumps(fake_donation))

        res_json = an.get_donation("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_donation)


class TestEmbeds:
    def test_get_embeds(self, requests_mock: Mocker, an: ActionNetwork, fake_embed: dict) -> None:
        req_url = f"{API_URL}/forms/123/embed"
        requests_mock.get(req_url, text=json.dumps(fake_embed))

        res_json = an.get_embeds("forms", "123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_embed)


class TestEventCampaigns:
    def test_get_event_campaigns(
        self, requests_mock: Mocker, an: ActionNetwork, fake_event_campaigns: dict
    ) -> None:
        req_url = f"{API_URL}/event_campaigns"
        requests_mock.get(req_url, text=json.dumps(fake_event_campaigns))

        res_json = an.get_event_campaigns(1)

        assert isinstance(res_json, Table)
        embedded = fake_event_campaigns["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_event_campaign(
        self, requests_mock: Mocker, an: ActionNetwork, fake_event_campaign: dict
    ) -> None:
        req_url = f"{API_URL}/event_campaigns/123"
        requests_mock.get(req_url, text=json.dumps(fake_event_campaign))

        res_json = an.get_event_campaign("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_event_campaign)

    def test_create_event_campaign(
        self, requests_mock: Mocker, an: ActionNetwork, fake_event_campaign: dict
    ) -> None:
        req_url = f"{API_URL}/event_campaigns"
        payload = {"title": "Canvassing Events", "origin_system": "AmyforTexas.com"}
        requests_mock.post(req_url, text=json.dumps(fake_event_campaign))

        res_json = an.create_event_campaign(payload)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_event_campaign)

    def test_create_event_in_event_campaign(
        self, requests_mock: Mocker, an: ActionNetwork, fake_event: dict
    ) -> None:
        req_url = f"{API_URL}/event_campaigns/123/events"
        payload = {"title": "My Canvassing Event", "origin_system": "CanvassingEvents.com"}
        requests_mock.post(req_url, text=json.dumps(fake_event))

        res_json = an.create_event_in_event_campaign("123", payload)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_event)

    def test_update_event_campaign(
        self, requests_mock: Mocker, an: ActionNetwork, fake_event_campaign: dict
    ) -> None:
        req_url = f"{API_URL}/event_campaigns/123"
        payload = {"description": "This is my new event campaign description"}
        requests_mock.put(req_url, text=json.dumps(fake_event_campaign))

        res_json = an.update_event_campaign("123", payload)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_event_campaign)


class TestEvents:
    def test_get_events(self, requests_mock: Mocker, an: ActionNetwork, fake_events: dict) -> None:
        req_url = f"{API_URL}/events"
        requests_mock.get(req_url, text=json.dumps(fake_events))

        res_json = an.get_events(1)

        assert isinstance(res_json, Table)
        embedded = fake_events["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_event_campaign_events(
        self, requests_mock: Mocker, an: ActionNetwork, fake_events: dict
    ) -> None:
        req_url = f"{API_URL}/event_campaigns/123/events"
        requests_mock.get(req_url, text=json.dumps(fake_events))

        res_json = an.get_event_campaign_events("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_events["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_event(self, requests_mock: Mocker, an: ActionNetwork, fake_event2: dict) -> None:
        req_url = f"{API_URL}/events/123"
        requests_mock.get(req_url, text=json.dumps(fake_event2))

        res_json = an.get_event("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_event2)

    def test_create_event(
        self,
        requests_mock: Mocker,
        an: ActionNetwork,
        fake_date: str,
        fake_event: dict,
        fake_location: dict,
    ) -> None:
        req_url = f"{API_URL}/events"
        requests_mock.post(req_url, text=json.dumps(fake_event))

        res_json = an.create_event("fake_title", start_date=fake_date, location=fake_location)

        assert isinstance(res_json, dict)
        assert res_json.items() == fake_event.items()


class TestForms:
    def test_get_forms(self, requests_mock: Mocker, an: ActionNetwork, fake_forms: dict) -> None:
        req_url = f"{API_URL}/forms"
        requests_mock.get(req_url, text=json.dumps(fake_forms))

        res_json = an.get_forms(1)

        assert isinstance(res_json, Table)
        embedded = fake_forms["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_form(self, requests_mock: Mocker, an: ActionNetwork, fake_form: dict) -> None:
        req_url = f"{API_URL}/forms/123"
        requests_mock.get(req_url, text=json.dumps(fake_form))

        res_json = an.get_form("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_form)

    def test_create_form(self, requests_mock: Mocker, an: ActionNetwork, fake_form: dict) -> None:
        payload = {"title": "My Free Form", "origin_system": "FreeForms.com"}
        req_url = f"{API_URL}/forms"
        requests_mock.post(req_url, text=json.dumps(fake_form))

        res_json = an.create_form(payload)

        assert isinstance(res_json, dict)
        assert res_json.items() == fake_form.items()

    def test_update_form(self, requests_mock: Mocker, an: ActionNetwork, fake_form: dict) -> None:
        req_url = f"{API_URL}/forms/123"
        payload = {"title": "My Free Form", "origin_system": "FreeForms.com"}
        requests_mock.put(req_url, text=json.dumps(fake_form))

        res_json = an.update_form("123", payload)

        assert isinstance(res_json, dict)
        assert res_json.items() == fake_form.items()


class TestFundraisingPages:
    def test_get_fundraising_pages(
        self, requests_mock: Mocker, an: ActionNetwork, fake_fundraising_pages: dict
    ) -> None:
        req_url = f"{API_URL}/fundraising_pages"
        requests_mock.get(req_url, text=json.dumps(fake_fundraising_pages))

        res_json = an.get_fundraising_pages(1)

        assert isinstance(res_json, Table)
        embedded = fake_fundraising_pages["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_fundraising_page(
        self, requests_mock: Mocker, an: ActionNetwork, fake_fundraising_page: dict
    ) -> None:
        req_url = f"{API_URL}/fundraising_pages/123"
        requests_mock.get(req_url, text=json.dumps(fake_fundraising_page))

        res_json = an.get_fundraising_page("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_fundraising_page)

    def test_create_fundraising_page(
        self, requests_mock: Mocker, an: ActionNetwork, fake_fundraising_page: dict
    ) -> None:
        req_url = f"{API_URL}/fundraising_pages"
        payload = {"title": "My Free Fundraiser", "origin_system": "FreeFundraisers.com"}
        requests_mock.post(req_url, text=json.dumps(fake_fundraising_page))

        res_json = an.create_fundraising_page(payload)

        assert isinstance(res_json, dict)
        assert res_json.items() == fake_fundraising_page.items()

    def test_update_fundraising_page(
        self, requests_mock: Mocker, an: ActionNetwork, fake_fundraising_page: dict
    ) -> None:
        req_url = f"{API_URL}/fundraising_pages/123"
        payload = {
            "title": "My Free Fundraiser With A New Name",
            "description": "This is my free fundraiser description",
        }
        requests_mock.put(req_url, text=json.dumps(fake_fundraising_page))

        res_json = an.update_fundraising_page("123", payload)

        assert isinstance(res_json, dict)
        assert res_json.items() == fake_fundraising_page.items()


class TestItems:
    def test_get_items(self, requests_mock: Mocker, an: ActionNetwork, fake_items: dict) -> None:
        req_url = f"{API_URL}/lists/123/items"
        requests_mock.get(req_url, text=json.dumps(fake_items))

        res_json = an.get_items("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_items["_embedded"]
        assert_matching_tables(an.get_items("123", 1), embedded[next(iter(embedded))])

    def test_get_item(self, requests_mock: Mocker, an: ActionNetwork, fake_item: dict) -> None:
        req_url = f"{API_URL}/lists/123/items/123"
        requests_mock.get(req_url, text=json.dumps(fake_item))
        assert_matching_tables(an.get_item("123", "123"), fake_item)


class TestLists:
    def test_get_lists(self, requests_mock: Mocker, an: ActionNetwork, fake_lists: dict) -> None:
        req_url = f"{API_URL}/lists"
        requests_mock.get(req_url, text=json.dumps(fake_lists))

        res_json = an.get_lists(1)

        assert isinstance(res_json, Table)
        embedded = fake_lists["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_list(self, requests_mock: Mocker, an: ActionNetwork, fake_list: dict) -> None:
        req_url = f"{API_URL}/lists/123"
        requests_mock.get(req_url, text=json.dumps(fake_list))

        res_json = an.get_list("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_list)


class TestMessages:
    def test_get_messages(
        self, requests_mock: Mocker, an: ActionNetwork, fake_messages: dict
    ) -> None:
        req_url = f"{API_URL}/messages"
        requests_mock.get(req_url, text=json.dumps(fake_messages))

        res_json = an.get_messages(1)

        assert isinstance(res_json, Table)
        embedded = fake_messages["_embedded"][next(iter(fake_messages["_embedded"]))]
        assert_matching_tables(res_json, embedded)

    def test_get_message(
        self, requests_mock: Mocker, an: ActionNetwork, fake_message: dict
    ) -> None:
        req_url = f"{API_URL}/messages/123"
        requests_mock.get(req_url, text=json.dumps(fake_message))

        res_json = an.get_message("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_message)

    def test_create_message(
        self, requests_mock: Mocker, an: ActionNetwork, fake_message: dict
    ) -> None:
        payload = {
            "subject": "Stop doing the bad thing",
            "body": "<p>The mayor should stop doing the bad thing.</p>",
            "from": "Progressive Action Now",
            "reply_to": "jane@progressiveactionnow.org",
            "targets": [{"href": f"{API_URL}/queries/123"}],
            "_links": {"osdi:wrapper": {"href": f"{API_URL}/wrappers/123"}},
        }
        req_url = f"{API_URL}/messages"
        requests_mock.post(req_url, text=json.dumps(fake_message))

        res_json = an.create_message(payload)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_message)

    def test_update_message(
        self, requests_mock: Mocker, an: ActionNetwork, fake_message: dict
    ) -> None:
        message_id = "123"
        payload = {
            "name": "Stop doing the bad thing email send 1",
            "subject": "Please! Stop doing the bad thing",
        }
        req_url = f"{API_URL}/messages/123"
        requests_mock.put(req_url, text=json.dumps(fake_message))
        assert_matching_tables(an.update_message(message_id, payload), fake_message)

    def test_schedule_message(self, requests_mock: Mocker, an: ActionNetwork) -> None:
        message_id = "123"
        scheduled_start_date = "2015-03-14T12:00:00Z"
        expected_response = {"message": "Your email has been scheduled."}
        req_url = f"{API_URL}/messages/123/schedule/"
        requests_mock.post(req_url, text=json.dumps(expected_response))

        res_json = an.schedule_message(message_id, scheduled_start_date)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, expected_response)

    def test_send_message(self, requests_mock: Mocker, an: ActionNetwork) -> None:
        message_id = "123"
        expected_response = {"message": "Your email has been sent."}
        req_url = f"{API_URL}/messages/123/send/"
        requests_mock.post(req_url, text=json.dumps(expected_response))

        res_json = an.send_message(message_id)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, expected_response)


class TestMetadata:
    def test_get_metadata(
        self, requests_mock: Mocker, an: ActionNetwork, fake_metadata: dict
    ) -> None:
        req_url = f"{API_URL}/metadata"
        requests_mock.get(req_url, text=json.dumps(fake_metadata))

        res_json = an.get_metadata()

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_metadata)


class TestOutreaches:
    def test_get_advocacy_campaign_outreaches(
        self, requests_mock: Mocker, an: ActionNetwork, fake_outreaches: dict
    ) -> None:
        requests_mock.get(
            f"{API_URL}/advocacy_campaigns/123/outreaches", text=json.dumps(fake_outreaches)
        )

        res_json = an.get_advocacy_campaign_outreaches("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_outreaches["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_person_outreaches(
        self, requests_mock: Mocker, an: ActionNetwork, fake_outreaches: dict
    ) -> None:
        req_url = f"{API_URL}/people/123/outreaches"
        requests_mock.get(req_url, text=json.dumps(fake_outreaches))

        res_json = an.get_person_outreaches("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_outreaches["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_advocacy_campaign_outreach(
        self, requests_mock: Mocker, an: ActionNetwork, fake_outreach: dict
    ) -> None:
        requests_mock.get(
            f"{API_URL}/advocacy_campaigns/123/outreaches/123", text=json.dumps(fake_outreach)
        )

        res_json = an.get_advocacy_campaign_outreach("123", "123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_outreach)

    def test_get_person_outreach(
        self, requests_mock: Mocker, an: ActionNetwork, fake_outreach: dict
    ) -> None:
        req_url = f"{API_URL}/people/123/outreaches/123"
        requests_mock.get(req_url, text=json.dumps(fake_outreach))

        res_json = an.get_person_outreach("123", "123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_outreach)

    def test_create_outreach(
        self,
        requests_mock: Mocker,
        an: ActionNetwork,
        fake_advocacy_campaign: dict,
        fake_outreach: dict,
    ) -> None:
        payload: dict = {
            "targets": [{"given_name": "Joe", "family_name": "Schmoe"}],
            "_links": {"osdi:person": {"href": f"{API_URL}/people/123"}},
        }
        campaign_id = next(iter(fake_advocacy_campaign["identifiers"])).split(":")[-1]
        requests_mock.post(
            f"{API_URL}/advocacy_campaigns/{campaign_id}/outreaches", text=json.dumps(fake_outreach)
        )

        res_json = an.create_outreach(campaign_id, payload)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_outreach)

    def test_update_outreach(
        self,
        requests_mock: Mocker,
        an: ActionNetwork,
        fake_advocacy_campaign: dict,
        fake_outreach: dict,
    ) -> None:
        payload = {"subject": "Please vote no!"}
        campaign_id = next(iter(fake_advocacy_campaign["identifiers"])).split(":")[-1]
        requests_mock.put(
            f"{API_URL}/advocacy_campaigns/{campaign_id}/outreaches/123",
            text=json.dumps(fake_outreach),
        )

        res_json = an.update_outreach(campaign_id, "123", payload)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_outreach)


class TestPeople:
    def test_get_people(
        self,
        requests_mock: Mocker,
        an: ActionNetwork,
        fake_people_list_1: dict,
        fake_people_list_2: dict,
        fake_people_list: list[dict],
    ) -> None:
        pages = (fake_people_list_1, fake_people_list_2, {"_embedded": {"osdi:people": []}})
        for pg_no, pg_data in enumerate(pages):
            req_url = f"{API_URL}/people?page={pg_no + 1}&per_page=25"
            requests_mock.get(req_url, text=json.dumps(pg_data))

        res_json = an.get_people()

        assert isinstance(res_json, Table)
        assert_matching_tables(res_json, Table(fake_people_list))

    def test_filter_get_people(
        self,
        requests_mock: Mocker,
        an: ActionNetwork,
        fake_filter_by_email_1: str,
        fake_people_list_1: dict,
        fake_people_list_2: dict,
        fake_people_list: list[dict],
    ) -> None:
        pages = (fake_people_list_1, fake_people_list_2, {"_embedded": {"osdi:people": []}})
        for pg_no, pg_data in enumerate(pages):
            req_url = f"{API_URL}/people?page={pg_no + 1}&per_page=25"
            requests_mock.get(req_url, text=json.dumps(pg_data))

        res_json = an.get_people(filter=fake_filter_by_email_1)

        assert isinstance(res_json, Table)
        assert_matching_tables(res_json, Table(fake_people_list))

    def test_get_person(
        self,
        requests_mock: Mocker,
        an: ActionNetwork,
        fake_person_id_1: str,
        fake_person: list[dict],
    ) -> None:
        req_url = f"{API_URL}/people/{fake_person_id_1}"
        requests_mock.get(req_url, text=json.dumps(fake_person))

        res_json = an.get_person(fake_person_id_1)

        assert isinstance(res_json, list)
        assert res_json == fake_person

    def test_upsert_person(
        self, requests_mock: Mocker, an: ActionNetwork, fake_upsert_person: dict
    ) -> None:
        req_url = f"{API_URL}/people"
        requests_mock.post(req_url, text=json.dumps(fake_upsert_person))

        res_json = an.upsert_person(**fake_upsert_person)

        assert isinstance(res_json, dict)
        assert res_json == fake_upsert_person

    def test_update_person(
        self,
        requests_mock: Mocker,
        an: ActionNetwork,
        fake_person_id_1: str,
        updated_fake_person: list[dict],
    ) -> None:
        requests_mock.put(
            f"{API_URL}/people/{fake_person_id_1}", text=json.dumps(updated_fake_person)
        )

        res_json = an.update_person(fake_person_id_1, given_name="Flake", family_name="McFlakerson")

        assert isinstance(res_json, list)
        assert res_json == updated_fake_person


class TestPetitions:
    def test_get_petitions(
        self, requests_mock: Mocker, an: ActionNetwork, fake_petitions: dict
    ) -> None:
        req_url = f"{API_URL}/petitions"
        requests_mock.get(req_url, text=json.dumps(fake_petitions))

        res_json = an.get_petitions(1)

        assert isinstance(res_json, Table)
        embedded = fake_petitions["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_petition(
        self, requests_mock: Mocker, an: ActionNetwork, fake_petition: dict
    ) -> None:
        req_url = f"{API_URL}/petitions/123"
        requests_mock.get(req_url, text=json.dumps(fake_petition))

        res_json = an.get_petition("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_petition)

    def test_create_petition(
        self, requests_mock: Mocker, an: ActionNetwork, fake_petition: dict
    ) -> None:
        fake_petition_data = {
            "title": fake_petition["title"],
            "description": fake_petition["description"],
            "petition_text": fake_petition["petition_text"],
            "target": fake_petition["target"],
        }
        req_url = f"{API_URL}/petitions"
        requests_mock.post(req_url, text=json.dumps(fake_petition_data))

        res_json = an.create_petition(
            fake_petition["title"],
            fake_petition["description"],
            fake_petition["petition_text"],
            fake_petition["target"],
        )

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_petition_data)

    def test_update_petition(
        self, requests_mock: Mocker, an: ActionNetwork, fake_petition: dict
    ) -> None:
        fake_petition_data = {
            "title": fake_petition["title"],
            "description": fake_petition["description"],
            "petition_text": fake_petition["petition_text"],
            "target": fake_petition["target"],
        }
        petition_id = next(iter(fake_petition["identifiers"])).split(":")[1]
        req_url = f"{API_URL}/petitions/{petition_id}"
        requests_mock.put(req_url, text=json.dumps(fake_petition_data))

        res_json = an.update_petition(
            petition_id,
            title=fake_petition["title"],
            description=fake_petition["description"],
            petition_text=fake_petition["petition_text"],
            target=fake_petition["target"],
        )

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_petition_data)


class TestQueries:
    def test_get_queries(
        self, requests_mock: Mocker, an: ActionNetwork, fake_queries: dict
    ) -> None:
        req_url = f"{API_URL}/queries"
        requests_mock.get(req_url, text=json.dumps(fake_queries))

        res_json = an.get_queries(1)

        assert isinstance(res_json, Table)
        embedded = fake_queries["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_query(self, requests_mock: Mocker, an: ActionNetwork, fake_query: dict) -> None:
        req_url = f"{API_URL}/queries/123"
        requests_mock.get(req_url, text=json.dumps(fake_query))

        res_json = an.get_query("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_query)


class TestSignatures:
    def test_get_petition_signatures(
        self, requests_mock: Mocker, an: ActionNetwork, fake_signatures: dict
    ) -> None:
        req_url = f"{API_URL}/petitions/123/signatures"
        requests_mock.get(req_url, text=json.dumps(fake_signatures))

        res_json = an.get_petition_signatures("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_signatures["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_person_signatures(
        self, requests_mock: Mocker, an: ActionNetwork, fake_signatures: dict
    ) -> None:
        req_url = f"{API_URL}/people/123/signatures"
        requests_mock.get(req_url, text=json.dumps(fake_signatures))

        res_json = an.get_person_signatures("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_signatures["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_petition_signature(
        self, requests_mock: Mocker, an: ActionNetwork, fake_signature: dict
    ) -> None:
        requests_mock.get(
            f"{API_URL}/petitions/123/signatures/123", text=json.dumps(fake_signature)
        )

        res_json = an.get_petition_signature("123", "123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_signature)

    def test_get_person_signature(
        self, requests_mock: Mocker, an: ActionNetwork, fake_signature: dict
    ) -> None:
        req_url = f"{API_URL}/people/123/signatures/123"
        requests_mock.get(req_url, text=json.dumps(fake_signature))

        res_json = an.get_person_signature("123", "123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_signature)

    def test_create_signature(
        self, requests_mock: Mocker, an: ActionNetwork, fake_signature: dict
    ) -> None:
        fake_signature_data = {
            "comments": fake_signature["comments"],
            "_links": {"osdi:person": {"href": fake_signature["_links"]["osdi:person"]["href"]}},
        }
        req_url = f"{API_URL}/petitions/456/signatures"
        requests_mock.post(req_url, text=json.dumps(fake_signature))

        res_json = an.create_signature("456", fake_signature_data)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_signature)

    def test_update_signature(
        self, requests_mock: Mocker, an: ActionNetwork, fake_signature: dict
    ) -> None:
        updated_signature_data = {"comments": "Updated comments"}
        requests_mock.put(
            f"{API_URL}/petitions/456/signatures/123", text=json.dumps(fake_signature)
        )

        res_json = an.update_signature("456", "123", updated_signature_data)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_signature)


class TestSubmissions:
    def test_get_form_submissions(
        self, requests_mock: Mocker, an: ActionNetwork, fake_submissions: dict
    ) -> None:
        req_url = f"{API_URL}/forms/123/submissions"
        requests_mock.get(req_url, text=json.dumps(fake_submissions))

        res_json = an.get_form_submissions("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_submissions["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_person_submissions(
        self, requests_mock: Mocker, an: ActionNetwork, fake_submissions: dict
    ) -> None:
        req_url = f"{API_URL}/people/123/submissions"
        requests_mock.get(req_url, text=json.dumps(fake_submissions))

        res_json = an.get_person_submissions("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_submissions["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_form_submission(
        self, requests_mock: Mocker, an: ActionNetwork, fake_submission: dict
    ) -> None:
        req_url = f"{API_URL}/forms/123/submissions/123"
        requests_mock.get(req_url, text=json.dumps(fake_submission))

        res_json = an.get_form_submission("123", "123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_submission)

    def test_get_person_submission(
        self, requests_mock: Mocker, an: ActionNetwork, fake_submission: dict
    ) -> None:
        req_url = f"{API_URL}/people/123/submissions/123"
        requests_mock.get(req_url, text=json.dumps(fake_submission))

        res_json = an.get_person_submission("123", "123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_submission)

    def test_create_submission(
        self, requests_mock: Mocker, an: ActionNetwork, fake_submission: dict
    ) -> None:
        req_url = f"{API_URL}/forms/123/submissions"
        requests_mock.post(req_url, text=json.dumps(fake_submission))

        assert_matching_tables(an.create_submission("123", "123"), fake_submission)

    def test_update_submission(
        self, requests_mock: Mocker, an: ActionNetwork, fake_submission: dict
    ) -> None:
        req_url = f"{API_URL}/forms/123/submissions/123"
        data = {"identifiers": ["other-system:230125s"]}
        requests_mock.put(req_url, json=data)

        assert_matching_tables(an.update_submission("123", "123", data), fake_submission)


class TestSurveys:
    def test_get_surveys(
        self, requests_mock: Mocker, an: ActionNetwork, fake_surveys: dict
    ) -> None:
        req_url = f"{API_URL}/surveys?page=1&per_page=25"
        requests_mock.get(req_url, text=json.dumps(fake_surveys))

        data = {"_embedded": {"action_network:surveys": []}}
        req_url = f"{API_URL}/surveys?page=2&per_page=25"
        requests_mock.get(req_url, text=json.dumps(data))

        assert_matching_tables(
            an.get_surveys(), Table(fake_surveys["_embedded"]["action_network:surveys"])
        )

    def test_get_survey(self, requests_mock: Mocker, an: ActionNetwork, fake_survey: dict) -> None:
        req_url = f"{API_URL}/surveys/123"
        requests_mock.get(req_url, text=json.dumps(fake_survey))

        assert_matching_tables(an.get_survey("123"), fake_survey)

    def test_create_survey(
        self, requests_mock: Mocker, an: ActionNetwork, fake_survey_payload: dict
    ) -> None:
        req_url = f"{API_URL}/surveys"
        requests_mock.post(req_url, text=json.dumps(fake_survey_payload))

        assert_matching_tables(an.create_survey(fake_survey_payload), fake_survey_payload)

    def test_update_survey(
        self, requests_mock: Mocker, an: ActionNetwork, fake_survey_payload: dict
    ) -> None:
        req_url = f"{API_URL}/surveys/123"
        requests_mock.post(req_url, text=json.dumps(fake_survey_payload))

        assert_matching_tables(an.update_survey("123", fake_survey_payload), fake_survey_payload)


class TestTags:
    def test_get_tags(self, requests_mock: Mocker, an: ActionNetwork, fake_tag_list: dict) -> None:
        req_url = f"{API_URL}/tags?page=1&per_page=25"
        requests_mock.get(req_url, text=json.dumps(fake_tag_list))
        requests_mock.get(
            f"{API_URL}/tags?page=2&per_page=25", text=json.dumps({"_embedded": {"osdi:tags": []}})
        )

        embedded = fake_tag_list["_embedded"]
        assert_matching_tables(an.get_tags(), Table(embedded["osdi:tags"]))

    def test_get_tag(
        self, requests_mock: Mocker, an: ActionNetwork, fake_tag_id_1: str, fake_tag: str
    ) -> None:
        req_url = f"{API_URL}/tags/{fake_tag_id_1}"
        requests_mock.get(req_url, text=json.dumps(fake_tag))

        assert an.get_tag(fake_tag_id_1) == fake_tag


class TestTaggings:
    def test_get_taggings(
        self, requests_mock: Mocker, an: ActionNetwork, fake_taggings: dict
    ) -> None:
        req_url = f"{API_URL}/tags/123/taggings"
        requests_mock.get(req_url, text=json.dumps(fake_taggings))

        res_json = an.get_taggings("123", 1)

        assert isinstance(res_json, Table)
        embedded = fake_taggings["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_tagging(
        self, requests_mock: Mocker, an: ActionNetwork, fake_tagging: dict
    ) -> None:
        req_url = f"{API_URL}/tags/123/taggings/123"
        requests_mock.get(req_url, text=json.dumps(fake_tagging))

        res_json = an.get_tagging("123", "123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_tagging)

    def test_create_tagging(
        self, requests_mock: Mocker, an: ActionNetwork, fake_tagging: dict
    ) -> None:
        req_url = f"{API_URL}/tags/123/taggings"
        requests_mock.post(req_url, json=fake_tagging)

        res_json = an.create_tagging("123", fake_tagging)

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_tagging)

    def test_delete_tagging(self, requests_mock: Mocker, an: ActionNetwork) -> None:
        expected_response = {"notice": "This tagging was successfully deleted."}
        req_url = f"{API_URL}/tags/123/taggings/123"
        requests_mock.delete(req_url, text=json.dumps(expected_response))

        res_json = an.delete_tagging("123", "123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, expected_response)


class TestWrappers:
    def test_get_wrappers(
        self, requests_mock: Mocker, an: ActionNetwork, fake_wrappers: dict
    ) -> None:
        req_url = f"{API_URL}/wrappers"
        requests_mock.get(req_url, text=json.dumps(fake_wrappers))

        res_json = an.get_wrappers(1)

        assert isinstance(res_json, Table)
        embedded = fake_wrappers["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_wrapper(
        self, requests_mock: Mocker, an: ActionNetwork, fake_wrapper: dict
    ) -> None:
        req_url = f"{API_URL}/wrappers/123"
        requests_mock.get(req_url, text=json.dumps(fake_wrapper))

        res_json = an.get_wrapper("123")

        assert isinstance(res_json, dict)
        assert_matching_tables(res_json, fake_wrapper)


class TestUniqueIDLists:
    def test_get_unique_id_lists(
        self, requests_mock: Mocker, an: ActionNetwork, fake_unique_id_lists: dict
    ) -> None:
        req_url = f"{API_URL}/unique_id_lists"
        requests_mock.get(req_url, text=json.dumps(fake_unique_id_lists))

        res_json = an.get_unique_id_lists(1)

        assert isinstance(res_json, Table)
        embedded = fake_unique_id_lists["_embedded"]
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_get_unique_id_list(
        self, requests_mock: Mocker, an: ActionNetwork, fake_unique_id_lists: dict
    ) -> None:
        embedded = fake_unique_id_lists["_embedded"]
        req_url = f"{API_URL}/unique_id_lists/123"
        data = embedded[next(iter(embedded))]
        requests_mock.get(req_url, text=json.dumps(data))

        res_json = an.get_unique_id_list("123")

        assert isinstance(res_json, list)
        assert_matching_tables(res_json, embedded[next(iter(embedded))])

    def test_create_unique_id_list(
        self, requests_mock: Mocker, an: ActionNetwork, fake_unique_id_list: dict
    ) -> None:
        req_url = f"{API_URL}/unique_id_lists"
        data = {
            "name": fake_unique_id_list["name"],
            "count": len(fake_unique_id_list["unique_ids"]),
        }
        requests_mock.post(req_url, text=json.dumps(data))

        res_json = an.create_unique_id_list(data["name"], fake_unique_id_list["unique_ids"])

        assert isinstance(res_json, dict)
        assert res_json["count"] == len(fake_unique_id_list["unique_ids"])
