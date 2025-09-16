import unittest

import pytest
import requests_mock

import test.test_mobilize.test_mobilize_json as test_json
from parsons import MobilizeAmerica
from test.utils import validate_list


class TestMobilizeAmerica(unittest.TestCase):
    def setUp(self):
        self.ma = MobilizeAmerica()

    def tearDown(self):
        pass

    def test_time_parse(self):
        # Test that Unix conversion works correctly
        assert self.ma._time_parse("<=2018-12-13") == "lte_1544659200"

        # Test that it throws an error when you put in an invalid filter
        date_filter_invalid = "=2018-12-01"
        with pytest.raises(ValueError, match=f"Unknown string format: {date_filter_invalid}"):
            self.ma._time_parse(date_filter_invalid)

    @requests_mock.Mocker()
    def test_get_organizations(self, m):
        m.get(self.ma.uri + "organizations", json=test_json.GET_ORGANIZATIONS_JSON)

        expected = [
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

        # Assert response is expected structure
        assert validate_list(expected, self.ma.get_organizations())

    @requests_mock.Mocker()
    def test_get_events(self, m):
        m.get(self.ma.uri + "events", json=test_json.GET_EVENTS_JSON)

        expected = [
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

        # Assert response is expected structure
        assert validate_list(expected, self.ma.get_events())

    @requests_mock.Mocker()
    def test__get_events_organization__can_exclude_timeslots(self, m):
        m.get(requests_mock.ANY, json=test_json.GET_EVENTS_ORGANIZATION_JSON)

        ma = MobilizeAmerica(api_key="test_password")
        data = ma.get_events_organization(1, max_timeslots=0)

        assert "timeslots_0_id" not in data.columns

    @requests_mock.Mocker()
    def test__get_events_organization__can_get_all_timeslots(self, m):
        m.get(requests_mock.ANY, json=test_json.GET_EVENTS_ORGANIZATION_JSON)

        ma = MobilizeAmerica(api_key="test_password")
        data = ma.get_events_organization(1)

        assert "timeslots_0_id" in data.columns
        assert "timeslots_1_id" in data.columns

    @requests_mock.Mocker()
    def test__get_events_organization__can_limit_timeslots(self, m):
        m.get(requests_mock.ANY, json=test_json.GET_EVENTS_ORGANIZATION_JSON)

        ma = MobilizeAmerica(api_key="test_password")
        data = ma.get_events_organization(1, max_timeslots=1)

        assert "timeslots_0_id" in data.columns
        assert "timeslots_1_id" not in data.columns

    @requests_mock.Mocker()
    def test_get_events_deleted(self, m):
        m.get(self.ma.uri + "events/deleted", json=test_json.GET_EVENTS_DELETED_JSON)

        # Assert response is expected structure
        assert validate_list(["id", "deleted_date"], self.ma.get_events_deleted())
