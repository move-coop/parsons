"""Tests for the MobilizeAmerica connector."""

import pytest
from requests_mock import ANY

from parsons import MobilizeAmerica
from test.conftest import validate_list

GET_ORGANIZATIONS_COLUMNS = [
    "id",
    "name",
    "slug",
    "is_coordinated",
    "is_independent",
    "is_primary_campaign",
    "state",
    "district",
    "candidate_name",
    "race_type",
    "event_feed_url",
    "created_date",
    "modified_date",
]

GET_EVENTS_COLUMNS = [
    "id",
    "description",
    "timezone",
    "title",
    "summary",
    "featured_image_url",
    "event_type",
    "created_date",
    "modified_date",
    "browser_url",
    "high_priority",
    "contact",
    "visibility",
    "sponsor_candidate_name",
    "sponsor_created_date",
    "sponsor_district",
    "sponsor_event_feed_url",
    "sponsor_id",
    "sponsor_is_coordinated",
    "sponsor_is_independent",
    "sponsor_is_primary_campaign",
    "sponsor_modified_date",
    "sponsor_name",
    "sponsor_race_type",
    "sponsor_slug",
    "sponsor_state",
    "address_lines",
    "congressional_district",
    "locality",
    "postal_code",
    "region",
    "state_leg_district",
    "state_senate_district",
    "venue",
    "latitude",
    "longitude",
    "timeslots_0_end_date",
    "timeslots_0_id",
    "timeslots_0_start_date",
]


def test_constructs_without_api_key(monkeypatch):
    """A key is optional at construction; only private endpoints require one."""
    monkeypatch.delenv("MOBILIZE_AMERICA_API_KEY", raising=False)

    ma = MobilizeAmerica()

    assert ma.api_key is None


def test_time_parse(mobilize):
    assert mobilize._time_parse("<=2018-12-13") == "lte_1544659200"


def test_time_parse_rejects_bad_filter(mobilize):
    with pytest.raises(ValueError, match="Unknown string format: =2018-12-01"):
        mobilize._time_parse("=2018-12-01")


def test_get_organizations(mobilize, requests_mock, load):
    requests_mock.get(mobilize.uri + "organizations", json=load("organizations"))

    assert validate_list(GET_ORGANIZATIONS_COLUMNS, mobilize.get_organizations())


def test_get_events(mobilize, requests_mock, load):
    requests_mock.get(mobilize.uri + "events", json=load("events"))

    assert validate_list(GET_EVENTS_COLUMNS, mobilize.get_events())


def test_get_events_organization_can_exclude_timeslots(requests_mock, load):
    requests_mock.get(ANY, json=load("events_organization"))
    ma = MobilizeAmerica(api_key="test_password")

    data = ma.get_events_organization(1, max_timeslots=0)

    assert "timeslots_0_id" not in data.columns


def test_get_events_organization_can_get_all_timeslots(requests_mock, load):
    requests_mock.get(ANY, json=load("events_organization"))
    ma = MobilizeAmerica(api_key="test_password")

    data = ma.get_events_organization(1)

    assert "timeslots_0_id" in data.columns
    assert "timeslots_1_id" in data.columns


def test_get_events_organization_can_limit_timeslots(requests_mock, load):
    requests_mock.get(ANY, json=load("events_organization"))
    ma = MobilizeAmerica(api_key="test_password")

    data = ma.get_events_organization(1, max_timeslots=1)

    assert "timeslots_0_id" in data.columns
    assert "timeslots_1_id" not in data.columns


def test_get_events_deleted(mobilize, requests_mock, load):
    requests_mock.get(mobilize.uri + "events/deleted", json=load("events_deleted"))

    assert validate_list(["id", "deleted_date"], mobilize.get_events_deleted())
