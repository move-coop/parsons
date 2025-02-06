import json
import logging
import os
import sys
import unittest

import requests_mock

from parsons import Copper, Table
from test.utils import assert_matching_tables

# Set up the logger
logger = logging.getLogger(__name__)

# Log to the console
strm_hdlr = logging.StreamHandler(sys.stdout)
strm_hdlr.setFormatter(logging.Formatter("%(message)s"))
strm_hdlr.setLevel(logging.DEBUG)
logger.addHandler(strm_hdlr)

logger.setLevel(logging.INFO)

_dir = os.path.dirname(__file__)

fake_search = [{"id": "fake"}]


class TestCopper(unittest.TestCase):
    def setUp(self):
        self.cp = Copper("usr@losr.fake", "key")

        # Using people as the most complicated object for test_get_standard_object()
        # Defined at self scope for use in test_get_people()
        self.processed_people = Table(
            [
                {
                    "id": 78757050,
                    "name": "Person One",
                    "prefix": None,
                    "first_name": "Person",
                    "middle_name": None,
                    "last_name": "One",
                    "suffix": None,
                    "assignee_id": None,
                    "company_id": 12030795,
                    "company_name": "Indivisible CityA",
                    "contact_type_id": 501950,
                    "details": None,
                    "tags": [],
                    "title": None,
                    "date_created": 1558169903,
                    "date_modified": 1558169910,
                    "date_last_contacted": 1558169891,
                    "interaction_count": 1,
                    "leads_converted_from": [],
                    "date_lead_created": None,
                    "address_city": "CityA",
                    "address_country": None,
                    "address_postal_code": "12345",
                    "address_state": "StateI",
                    "address_street": None,
                },
                {
                    "id": 78477076,
                    "name": "Person Two",
                    "prefix": None,
                    "first_name": "Person",
                    "middle_name": None,
                    "last_name": "Two",
                    "suffix": None,
                    "assignee_id": 289533,
                    "company_id": 12096071,
                    "company_name": "Indivisible StateII",
                    "contact_type_id": 501950,
                    "details": None,
                    "tags": ["treasurer"],
                    "title": "Treasurer",
                    "date_created": 1557761054,
                    "date_modified": 1558218799,
                    "date_last_contacted": 1558196341,
                    "interaction_count": 14,
                    "leads_converted_from": [],
                    "date_lead_created": None,
                    "address_city": None,
                    "address_country": None,
                    "address_postal_code": None,
                    "address_state": None,
                    "address_street": None,
                },
                {
                    "id": 78839154,
                    "name": "Person Three",
                    "prefix": None,
                    "first_name": "Person",
                    "middle_name": None,
                    "last_name": "Three",
                    "suffix": None,
                    "assignee_id": None,
                    "company_id": 34966944,
                    "company_name": "Flip StateIII",
                    "contact_type_id": 501950,
                    "details": None,
                    "tags": [],
                    "title": None,
                    "date_created": 1558223367,
                    "date_modified": 1558223494,
                    "date_last_contacted": 1558223356,
                    "interaction_count": 2,
                    "leads_converted_from": [],
                    "date_lead_created": None,
                    "address_city": "CityC",
                    "address_country": None,
                    "address_postal_code": "54321",
                    "address_state": "StateIII",
                    "address_street": None,
                },
            ]
        )

        # Tables and table names for test_get_custom_fields() and test_process_custom_fields()
        self.custom_field_tables = {}
        self.custom_field_table_names = [
            "custom_fields",
            "custom_fields_available",
            "custom_fields_options",
        ]

        self.custom_field_tables["custom_fields"] = Table(
            [
                {"id": 101674, "name": "Event Date", "data_type": "Date"},
                {"id": 102127, "name": "Date Added", "data_type": "Date"},
                {"id": 109116, "name": "Local Group Subtype", "data_type": "Dropdown"},
            ]
        )

        self.custom_field_tables["custom_fields_available"] = Table(
            [
                {"id": 101674, "available_on": "opportunity"},
                {"id": 102127, "available_on": "company"},
                {"id": 102127, "available_on": "person"},
                {"id": 109116, "available_on": "company"},
            ]
        )

        self.custom_field_tables["custom_fields_options"] = Table(
            [
                {
                    "id": 109116,
                    "name": "Local Group Subtype",
                    "options_id": 140251,
                    "options_name": "Public (displayed in map)",
                    "options_rank": 0,
                },
                {
                    "id": 109116,
                    "name": "Local Group Subtype",
                    "options_id": 140250,
                    "options_name": "New (Needs Processing)",
                    "options_rank": 4,
                },
                {
                    "id": 109116,
                    "name": "Local Group Subtype",
                    "options_id": 140252,
                    "options_name": "Private (not on map)",
                    "options_rank": 1,
                },
                {
                    "id": 109116,
                    "name": "Local Group Subtype",
                    "options_id": 140254,
                    "options_name": "National",
                    "options_rank": 5,
                },
                {
                    "id": 109116,
                    "name": "Local Group Subtype",
                    "options_id": 140766,
                    "options_name": "Not following principles",
                    "options_rank": 3,
                },
                {
                    "id": 109116,
                    "name": "Local Group Subtype",
                    "options_id": 140764,
                    "options_name": "International",
                    "options_rank": 6,
                },
                {
                    "id": 109116,
                    "name": "Local Group Subtype",
                    "options_id": 141434,
                    "options_name": "Inactive",
                    "options_rank": 2,
                },
            ]
        )

    def test_init(self):
        self.assertEqual(self.cp.user_email, "usr@losr.fake")
        self.assertEqual(self.cp.api_key, "key")

    @requests_mock.Mocker()
    def test_base_request(self, m):
        # Assert the fake_search dict is returned
        m.post(self.cp.uri + "/people/search", json=fake_search)
        self.assertEqual(
            fake_search,
            json.loads(self.cp.base_request("/people/search", req_type="POST").text),
        )

    def paginate_callback(self, request, context):
        # Internal method for simulating pagination

        context.status_code = 200

        # GET request.text is always None
        if request.text is None:
            row_start = 0
            row_finish = 100
        else:
            pdict = json.loads(request.text)
            page_number = pdict["page_number"] - 1
            page_size = pdict["page_size"]

            row_start = page_number * page_size
            row_finish = row_start + page_size

        with open(f"{_dir}/{context.headers['filename']}", "r") as json_file:
            response = json.load(json_file)

        if isinstance(response, list):
            context.headers["X-Pw-Total"] = str(len(response))
            return response[row_start:row_finish]
        else:
            return response

    @requests_mock.Mocker()
    def test_paginate_request(self, m):
        # Anonymized real output with nested columns
        self.blob = [
            {
                "id": 78757050,
                "name": "Person One",
                "prefix": None,
                "first_name": "Person",
                "middle_name": None,
                "last_name": "One",
                "suffix": None,
                "address": {
                    "street": None,
                    "city": "CityA",
                    "state": "StateI",
                    "postal_code": "12345",
                    "country": None,
                },
                "assignee_id": None,
                "company_id": 12030795,
                "company_name": "Indivisible CityA",
                "contact_type_id": 501950,
                "details": None,
                "emails": [{"email": "PersonOne@fakemail.nope", "category": "work"}],
                "phone_numbers": [
                    {"number": "(541) 555-9585", "category": "work"},
                    {"number": "555-555-9585", "category": "work"},
                ],
                "socials": [{"url": "https://gravatar.com/gravatar", "category": "gravatar"}],
                "tags": [],
                "title": None,
                "websites": [{"url": "http://www.IndivisibleCityA.org", "category": None}],
                "custom_fields": [
                    {"custom_field_definition_id": 125880, "value": None},
                    {"custom_field_definition_id": 107297, "value": None},
                    {"custom_field_definition_id": 102127, "value": None},
                    {"custom_field_definition_id": 135034, "value": None},
                    {"custom_field_definition_id": 107298, "value": None},
                    {"custom_field_definition_id": 108972, "value": None},
                    {"custom_field_definition_id": 125881, "value": None},
                ],
                "date_created": 1558169903,
                "date_modified": 1558169910,
                "date_last_contacted": 1558169891,
                "interaction_count": 1,
                "leads_converted_from": [],
                "date_lead_created": None,
            },
            {
                "id": 78477076,
                "name": "Person Two",
                "prefix": None,
                "first_name": "Person",
                "middle_name": None,
                "last_name": "Two",
                "suffix": None,
                "address": {
                    "street": None,
                    "city": None,
                    "state": None,
                    "postal_code": None,
                    "country": None,
                },
                "assignee_id": 289533,
                "company_id": 12096071,
                "company_name": "Indivisible StateII",
                "contact_type_id": 501950,
                "details": None,
                "emails": [{"email": "Personb23@gmail.com", "category": "work"}],
                "phone_numbers": [{"number": "(908) 555-2941", "category": "work"}],
                "socials": [],
                "tags": ["treasurer"],
                "title": "Treasurer",
                "websites": [],
                "custom_fields": [
                    {"custom_field_definition_id": 125880, "value": None},
                    {"custom_field_definition_id": 107297, "value": None},
                    {"custom_field_definition_id": 102127, "value": None},
                    {"custom_field_definition_id": 135034, "value": None},
                    {"custom_field_definition_id": 107298, "value": None},
                    {"custom_field_definition_id": 108972, "value": None},
                    {"custom_field_definition_id": 125881, "value": None},
                ],
                "date_created": 1557761054,
                "date_modified": 1558218799,
                "date_last_contacted": 1558196341,
                "interaction_count": 14,
                "leads_converted_from": [],
                "date_lead_created": None,
            },
            {
                "id": 78839154,
                "name": "Person Three",
                "prefix": None,
                "first_name": "Person",
                "middle_name": None,
                "last_name": "Three",
                "suffix": None,
                "address": {
                    "street": None,
                    "city": "CityC",
                    "state": "StateIII",
                    "postal_code": "54321",
                    "country": None,
                },
                "assignee_id": None,
                "company_id": 34966944,
                "company_name": "Flip StateIII",
                "contact_type_id": 501950,
                "details": None,
                "emails": [{"email": "Person.Three@fakemail.nope", "category": "work"}],
                "phone_numbers": [{"number": "(619) 555-7883", "category": "work"}],
                "socials": [
                    {"url": "https://twitter.com/ThreePerson", "category": "twitter"},
                    {
                        "url": "https://www.facebook.com/Person.n.Three",
                        "category": "facebook",
                    },
                    {"url": "https://gravatar.com/PersonThree", "category": "gravatar"},
                ],
                "tags": [],
                "title": None,
                "websites": [],
                "custom_fields": [
                    {"custom_field_definition_id": 125880, "value": None},
                    {"custom_field_definition_id": 107297, "value": None},
                    {"custom_field_definition_id": 102127, "value": None},
                    {"custom_field_definition_id": 135034, "value": None},
                    {"custom_field_definition_id": 107298, "value": None},
                    {"custom_field_definition_id": 108972, "value": None},
                    {"custom_field_definition_id": 125881, "value": None},
                ],
                "date_created": 1558223367,
                "date_modified": 1558223494,
                "date_last_contacted": 1558223356,
                "interaction_count": 2,
                "leads_converted_from": [],
                "date_lead_created": None,
            },
        ]

        # Mock endpoints
        m.post(
            self.cp.uri + "/people/search",
            json=self.paginate_callback,
            headers={"filename": "people_search.txt"},
        )

        # self.assertTrue(
        assert_matching_tables(
            Table(self.blob),
            Table(self.cp.paginate_request("/people/search", page_size=1, req_type="POST")),
        )

    def test_process_json(self):
        # Stress-testing combination of unpack methods with contrived table from hell
        fake_response = [
            {
                "id": 1,
                "Simple List Col": ["one", "two", "three"],
                "Mixed List Col": [None, 2, "three"],
                "Spotty List Col": [1, 2, 3],
                "Multidim List Col": [[1, 2], [None, "two"], []],
                "Nested List Col": [
                    {"A": 1, "B": "one"},
                    {"A": 2, "B": "two"},
                    {"A": 3, "B": "three"},
                ],
                "Simple Dict Col": {"one": 1, "two": 2, "three": 3},
                "Nested Dict Col": {"A": 1, "B": ["two", 2], "C": [None, 3, "three"]},
            },
            {
                "id": 2,
                "Simple List Col": ["four", "five", "six"],
                "Mixed List Col": ["four", None, 6],
                "Spotty List Col": [],
                "Multidim List Col": [[3, None], [], ["three", "four"]],
                "Nested List Col": [
                    {"A": 4, "B": "four"},
                    {"A": 5, "B": "five"},
                    {"A": 6, "B": "six"},
                ],
                "Simple Dict Col": {"one": "I", "two": "II", "three": "III"},
                "Nested Dict Col": {"A": ["one"], "B": [], "C": 3},
            },
            {
                "id": 3,
                "Simple List Col": ["seven", "eight", "nine"],
                "Mixed List Col": [7, "eight", None],
                "Spotty List Col": None,
                "Multidim List Col": [["five", 6], [None]],
                "Nested List Col": [
                    {"A": 7, "B": "seven"},
                    {"A": 8, "B": "eight"},
                    {"A": 9, "B": "nine"},
                ],
                "Simple Dict Col": {"one": "x", "two": "xx", "three": "xxx"},
                "Nested Dict Col": {"A": None, "B": 2, "C": [None, 3, "three"]},
            },
        ]

        fake_response_tables = {}
        table_names = ["fake_Nested List Col", "fake"]

        fake_response_tables["fake_Nested List Col"] = Table(
            [
                {"id": 1, "Nested List Col_A": 1, "Nested List Col_B": "one"},
                {"id": 1, "Nested List Col_A": 2, "Nested List Col_B": "two"},
                {"id": 1, "Nested List Col_A": 3, "Nested List Col_B": "three"},
                {"id": 2, "Nested List Col_A": 4, "Nested List Col_B": "four"},
                {"id": 2, "Nested List Col_A": 5, "Nested List Col_B": "five"},
                {"id": 2, "Nested List Col_A": 6, "Nested List Col_B": "six"},
                {"id": 3, "Nested List Col_A": 7, "Nested List Col_B": "seven"},
                {"id": 3, "Nested List Col_A": 8, "Nested List Col_B": "eight"},
                {"id": 3, "Nested List Col_A": 9, "Nested List Col_B": "nine"},
            ]
        )

        fake_response_tables["fake"] = Table(
            [
                {
                    "id": 1,
                    "Simple List Col": ["one", "two", "three"],
                    "Mixed List Col": [None, 2, "three"],
                    "Spotty List Col": [1, 2, 3],
                    "Multidim List Col": [[1, 2], [None, "two"], []],
                    "Simple Dict Col_one": 1,
                    "Simple Dict Col_three": 3,
                    "Simple Dict Col_two": 2,
                    "Nested Dict Col_A": 1,
                    "Nested Dict Col_B": ["two", 2],
                    "Nested Dict Col_C": [None, 3, "three"],
                },
                {
                    "id": 2,
                    "Simple List Col": ["four", "five", "six"],
                    "Mixed List Col": ["four", None, 6],
                    "Spotty List Col": [],
                    "Multidim List Col": [[3, None], [], ["three", "four"]],
                    "Simple Dict Col_one": "I",
                    "Simple Dict Col_three": "III",
                    "Simple Dict Col_two": "II",
                    "Nested Dict Col_A": ["one"],
                    "Nested Dict Col_B": [],
                    "Nested Dict Col_C": 3,
                },
                {
                    "id": 3,
                    "Simple List Col": ["seven", "eight", "nine"],
                    "Mixed List Col": [7, "eight", None],
                    "Spotty List Col": [None],
                    "Multidim List Col": [["five", 6], [None]],
                    "Simple Dict Col_one": "x",
                    "Simple Dict Col_three": "xxx",
                    "Simple Dict Col_two": "xx",
                    "Nested Dict Col_A": None,
                    "Nested Dict Col_B": 2,
                    "Nested Dict Col_C": [None, 3, "three"],
                },
            ]
        )

        fake_processed = self.cp.process_json(fake_response, "fake")
        self.assertTrue([f["name"] for f in fake_processed] == table_names)
        for tbl in table_names:
            assert_matching_tables(
                [f["tbl"] for f in fake_processed if f["name"] == tbl][0],
                fake_response_tables[tbl],
            )

        fake_tidy = self.cp.process_json(fake_response, "fake", tidy=0)
        self.assertTrue(len(fake_tidy) == len(fake_response[0]) - 1)

    def test_process_custom_fields(self):
        # Using same json file and processed data in testing both process_ and get_ methods

        with open(f"{_dir}/custom_fields_search.json", "r") as json_file:
            fake_response = json.load(json_file)

        fake_processed = self.cp.process_custom_fields(fake_response)
        self.assertTrue([f["name"] for f in fake_processed] == self.custom_field_table_names)
        for tbl in self.custom_field_table_names:
            assert_matching_tables(
                [f["tbl"] for f in fake_processed if f["name"] == tbl][0],
                self.custom_field_tables[tbl],
            )

    @requests_mock.Mocker()
    def test_get_standard_object(self, m):
        processed_people_emails = Table(
            [
                {
                    "id": 78757050,
                    "emails_category": "work",
                    "emails_email": "PersonOne@fakemail.nope",
                },
                {
                    "id": 78477076,
                    "emails_category": "work",
                    "emails_email": "Personb23@gmail.com",
                },
                {
                    "id": 78839154,
                    "emails_category": "work",
                    "emails_email": "Person.Three@fakemail.nope",
                },
            ]
        )

        m.post(
            self.cp.uri + "/people/search",
            json=self.paginate_callback,
            headers={"filename": "people_search.txt"},
        )

        # Object-specific get_ functions are just wrappers for get_standard_object()
        # So the following line is the only difference from test_get_people()
        processed_blob = self.cp.get_standard_object("people")
        blob_people = [f for f in processed_blob if f["name"] == "people"][0]["tbl"]
        blob_people_emails = [f for f in processed_blob if f["name"] == "people_emails"][0]["tbl"]

        assert_matching_tables(self.processed_people, blob_people)
        assert_matching_tables(processed_people_emails, blob_people_emails)

    @requests_mock.Mocker()
    def test_get_people(self, m):
        processed_people_emails = Table(
            [
                {
                    "id": 78757050,
                    "emails_category": "work",
                    "emails_email": "PersonOne@fakemail.nope",
                },
                {
                    "id": 78477076,
                    "emails_category": "work",
                    "emails_email": "Personb23@gmail.com",
                },
                {
                    "id": 78839154,
                    "emails_category": "work",
                    "emails_email": "Person.Three@fakemail.nope",
                },
            ]
        )

        m.post(
            self.cp.uri + "/people/search",
            json=self.paginate_callback,
            headers={"filename": "people_search.txt"},
        )
        processed_blob = self.cp.get_people()
        blob_people = [f for f in processed_blob if f["name"] == "people"][0]["tbl"]
        blob_people_emails = [f for f in processed_blob if f["name"] == "people_emails"][0]["tbl"]

        # Actually testing get_standard_object() and process_json()
        # Dicts & simple lists are unpacked to columns on original table
        # People tables matching means this worked
        assert_matching_tables(self.processed_people, blob_people)

        # Lists of dicts are unpacked to long tables
        # People_emails tables are one example (good enough)
        assert_matching_tables(processed_people_emails, blob_people_emails)

    @requests_mock.Mocker()
    def test_get_opportunities(self, m):
        processed_opps = Table(
            [
                {
                    "id": 14340759,
                    "name": "Company1",
                    "assignee_id": 659394,
                    "close_date": None,
                    "company_id": 29324143,
                    "company_name": "Company1",
                    "customer_source_id": None,
                    "details": None,
                    "loss_reason_id": None,
                    "pipeline_id": 489028,
                    "pipeline_stage_id": 2529569,
                    "primary_contact_id": 67747998,
                    "priority": "High",
                    "status": "Open",
                    "tags": ["opportunities import-1540158946352"],
                    "interaction_count": 0,
                    "monetary_unit": "USD",
                    "monetary_value": 100000.0,
                    "converted_unit": None,
                    "converted_value": None,
                    "win_probability": None,
                    "date_stage_changed": 1548866182,
                    "date_last_contacted": None,
                    "leads_converted_from": [],
                    "date_lead_created": None,
                    "date_created": 1540159060,
                    "date_modified": 1550858334,
                },
                {
                    "id": 14161592,
                    "name": "Company2",
                    "assignee_id": 659394,
                    "close_date": "11/10/2018",
                    "company_id": 28729196,
                    "company_name": "Company2",
                    "customer_source_id": None,
                    "details": None,
                    "loss_reason_id": None,
                    "pipeline_id": 531482,
                    "pipeline_stage_id": 2607171,
                    "primary_contact_id": 67243374,
                    "priority": "High",
                    "status": "Open",
                    "tags": [],
                    "interaction_count": 36,
                    "monetary_unit": "USD",
                    "monetary_value": 77000.0,
                    "converted_unit": None,
                    "converted_value": None,
                    "win_probability": None,
                    "date_stage_changed": 1551191957,
                    "date_last_contacted": 1552339800,
                    "leads_converted_from": [],
                    "date_lead_created": None,
                    "date_created": 1539192375,
                    "date_modified": 1552340016,
                },
                {
                    "id": 14286548,
                    "name": "Company3",
                    "assignee_id": 644608,
                    "close_date": "11/18/2018",
                    "company_id": 29492294,
                    "company_name": "Company3",
                    "customer_source_id": None,
                    "details": None,
                    "loss_reason_id": None,
                    "pipeline_id": 531482,
                    "pipeline_stage_id": 2482007,
                    "primary_contact_id": 67637400,
                    "priority": "None",
                    "status": "Open",
                    "tags": [],
                    "interaction_count": 19,
                    "monetary_unit": "USD",
                    "monetary_value": 150000.0,
                    "converted_unit": None,
                    "converted_value": None,
                    "win_probability": 0,
                    "date_stage_changed": 1539870749,
                    "date_last_contacted": 1555534313,
                    "leads_converted_from": [],
                    "date_lead_created": None,
                    "date_created": 1539870749,
                    "date_modified": 1555550658,
                },
            ]
        )

        processed_opps_cf = Table(
            [
                {
                    "id": 14340759,
                    "custom_fields_custom_field_definition_id": 272931,
                    "custom_fields_value": [],
                },
                {
                    "id": 14340759,
                    "custom_fields_custom_field_definition_id": 272927,
                    "custom_fields_value": None,
                },
                {
                    "id": 14161592,
                    "custom_fields_custom_field_definition_id": 272931,
                    "custom_fields_value": [],
                },
                {
                    "id": 14161592,
                    "custom_fields_custom_field_definition_id": 272927,
                    "custom_fields_value": None,
                },
                {
                    "id": 14286548,
                    "custom_fields_custom_field_definition_id": 272931,
                    "custom_fields_value": [],
                },
                {
                    "id": 14286548,
                    "custom_fields_custom_field_definition_id": 272927,
                    "custom_fields_value": None,
                },
            ]
        )

        m.post(
            self.cp.uri + "/opportunities/search",
            json=self.paginate_callback,
            headers={"filename": "opportunities_search.json"},
        )

        processed_blob = self.cp.get_opportunities()
        blob_opps = [f for f in processed_blob if f["name"] == "opportunities"][0]["tbl"]
        blob_opps_cf = [f for f in processed_blob if f["name"] == "opportunities_custom_fields"]
        blob_opps_cf = blob_opps_cf[0]["tbl"]

        assert_matching_tables(processed_opps, blob_opps)
        assert_matching_tables(processed_opps_cf, blob_opps_cf)

    @requests_mock.Mocker()
    def test_get_opportunities2(self, m):
        processed_opps = Table(
            [
                {
                    "id": 14340759,
                    "name": "Company1",
                    "assignee_id": 659394,
                    "close_date": None,
                    "company_id": 29324143,
                    "company_name": "Company1",
                    "customer_source_id": None,
                    "details": None,
                    "loss_reason_id": None,
                    "pipeline_id": 489028,
                    "pipeline_stage_id": 2529569,
                    "primary_contact_id": 67747998,
                    "priority": "High",
                    "status": "Open",
                    "tags": ["opportunities import-1540158946352"],
                    "interaction_count": 0,
                    "monetary_unit": "USD",
                    "monetary_value": 100000.0,
                    "converted_unit": None,
                    "converted_value": None,
                    "win_probability": None,
                    "date_stage_changed": 1548866182,
                    "date_last_contacted": None,
                    "leads_converted_from": [],
                    "date_lead_created": None,
                    "date_created": 1540159060,
                    "date_modified": 1550858334,
                },
                {
                    "id": 14161592,
                    "name": "Company2",
                    "assignee_id": 659394,
                    "close_date": "11/10/2018",
                    "company_id": 28729196,
                    "company_name": "Company2",
                    "customer_source_id": None,
                    "details": None,
                    "loss_reason_id": None,
                    "pipeline_id": 531482,
                    "pipeline_stage_id": 2607171,
                    "primary_contact_id": 67243374,
                    "priority": "High",
                    "status": "Open",
                    "tags": [],
                    "interaction_count": 36,
                    "monetary_unit": "USD",
                    "monetary_value": 77000.0,
                    "converted_unit": None,
                    "converted_value": None,
                    "win_probability": None,
                    "date_stage_changed": 1551191957,
                    "date_last_contacted": 1552339800,
                    "leads_converted_from": [],
                    "date_lead_created": None,
                    "date_created": 1539192375,
                    "date_modified": 1552340016,
                },
                {
                    "id": 14286548,
                    "name": "Company3",
                    "assignee_id": 644608,
                    "close_date": "11/18/2018",
                    "company_id": 29492294,
                    "company_name": "Company3",
                    "customer_source_id": None,
                    "details": None,
                    "loss_reason_id": None,
                    "pipeline_id": 531482,
                    "pipeline_stage_id": 2482007,
                    "primary_contact_id": 67637400,
                    "priority": "None",
                    "status": "Open",
                    "tags": [],
                    "interaction_count": 19,
                    "monetary_unit": "USD",
                    "monetary_value": 150000.0,
                    "converted_unit": None,
                    "converted_value": None,
                    "win_probability": 0,
                    "date_stage_changed": 1539870749,
                    "date_last_contacted": 1555534313,
                    "leads_converted_from": [],
                    "date_lead_created": None,
                    "date_created": 1539870749,
                    "date_modified": 1555550658,
                },
            ]
        )

        processed_opps_cf = Table(
            [
                {
                    "id": 14340759,
                    "custom_fields_custom_field_definition_id": 272931,
                    "custom_fields_value": [],
                },
                {
                    "id": 14340759,
                    "custom_fields_custom_field_definition_id": 272927,
                    "custom_fields_value": None,
                },
                {
                    "id": 14161592,
                    "custom_fields_custom_field_definition_id": 272931,
                    "custom_fields_value": [],
                },
                {
                    "id": 14161592,
                    "custom_fields_custom_field_definition_id": 272927,
                    "custom_fields_value": None,
                },
                {
                    "id": 14286548,
                    "custom_fields_custom_field_definition_id": 272931,
                    "custom_fields_value": [],
                },
                {
                    "id": 14286548,
                    "custom_fields_custom_field_definition_id": 272927,
                    "custom_fields_value": None,
                },
            ]
        )

        m.post(
            self.cp.uri + "/opportunities/search",
            json=self.paginate_callback,
            headers={"filename": "opportunities_search.json"},
        )

        processed_blob = self.cp.get_opportunities()
        blob_opps = [f for f in processed_blob if f["name"] == "opportunities"][0]["tbl"]
        blob_opps_cf = [f for f in processed_blob if f["name"] == "opportunities_custom_fields"]
        blob_opps_cf = blob_opps_cf[0]["tbl"]

        assert_matching_tables(processed_opps, blob_opps)
        assert_matching_tables(processed_opps_cf, blob_opps_cf)

    @requests_mock.Mocker()
    def test_get_companies(self, m):
        processed_companies = Table(
            [
                {
                    "id": 35015567,
                    "name": "Company One",
                    "assignee_id": None,
                    "contact_type_id": 547508,
                    "details": None,
                    "email_domain": "companyone@fake.nope",
                    "tags": [],
                    "interaction_count": 1,
                    "date_created": 1558441519,
                    "date_modified": 1558441535,
                    "address_city": "CityA",
                    "address_country": None,
                    "address_postal_code": "12345",
                    "address_state": "New York",
                    "address_street": None,
                },
                {
                    "id": 35026533,
                    "name": "Company Two",
                    "assignee_id": None,
                    "contact_type_id": 547508,
                    "details": None,
                    "email_domain": "companytwo@fake.nope",
                    "tags": [],
                    "interaction_count": 1,
                    "date_created": 1558452953,
                    "date_modified": 1558452967,
                    "address_city": "CityB",
                    "address_country": None,
                    "address_postal_code": "23451",
                    "address_state": "New York",
                    "address_street": None,
                },
                {
                    "id": 35014973,
                    "name": "Company Three",
                    "assignee_id": None,
                    "contact_type_id": 547508,
                    "details": None,
                    "email_domain": None,
                    "tags": [],
                    "interaction_count": 1,
                    "date_created": 1558434147,
                    "date_modified": 1558458137,
                    "address_city": None,
                    "address_country": None,
                    "address_postal_code": "34512",
                    "address_state": "Alabama",
                    "address_street": None,
                },
                {
                    "id": 35029116,
                    "name": "Company Four",
                    "assignee_id": None,
                    "contact_type_id": 547508,
                    "details": None,
                    "email_domain": "companyfour@fake.nope",
                    "tags": [],
                    "interaction_count": 0,
                    "date_created": 1558461301,
                    "date_modified": 1558461301,
                    "address_city": "CityD ",
                    "address_country": None,
                    "address_postal_code": "45123",
                    "address_state": "California",
                    "address_street": None,
                },
                {
                    "id": 35082308,
                    "name": "Company Five",
                    "assignee_id": None,
                    "contact_type_id": 547508,
                    "details": None,
                    "email_domain": "companyfive@fake.nope",
                    "tags": [],
                    "interaction_count": 1,
                    "date_created": 1558639445,
                    "date_modified": 1558639459,
                    "address_city": "CityE",
                    "address_country": None,
                    "address_postal_code": "51234",
                    "address_state": "Arizona",
                    "address_street": None,
                },
            ]
        )

        processed_companies_phones = Table(
            [
                {
                    "id": 35082308,
                    "phone_numbers_category": "work",
                    "phone_numbers_number": "123-555-9876",
                }
            ]
        )

        m.post(
            self.cp.uri + "/companies/search",
            json=self.paginate_callback,
            headers={"filename": "companies_search.json"},
        )

        processed_blob = self.cp.get_companies()
        blob_companies = [f for f in processed_blob if f["name"] == "companies"][0]["tbl"]
        blob_companies_phones = [
            f for f in processed_blob if f["name"] == "companies_phone_numbers"
        ][0]["tbl"]

        assert_matching_tables(processed_companies, blob_companies)
        assert_matching_tables(processed_companies_phones, blob_companies_phones)

    @requests_mock.Mocker()
    def test_get_activities(self, m):
        processed_activities = Table(
            [
                {
                    "id": 5369412841,
                    "user_id": 289533,
                    "details": None,
                    "activity_date": 1554149472,
                    "old_value": None,
                    "new_value": None,
                    "date_created": 1554149472,
                    "date_modified": 1554149472,
                    "parent_id": 76469872,
                    "parent_type": "person",
                    "type_category": "system",
                    "type_id": 1,
                },
                {
                    "id": 5223481640,
                    "user_id": 377343,
                    "details": None,
                    "activity_date": 1550789277,
                    "old_value": None,
                    "new_value": None,
                    "date_created": 1550789277,
                    "date_modified": 1550789277,
                    "parent_id": 28465522,
                    "parent_type": "person",
                    "type_category": "system",
                    "type_id": 1,
                },
                {
                    "id": 5185524266,
                    "user_id": 703426,
                    "details": None,
                    "activity_date": 1549983210,
                    "old_value": None,
                    "new_value": None,
                    "date_created": 1549983210,
                    "date_modified": 1549983210,
                    "parent_id": 12035585,
                    "parent_type": "company",
                    "type_category": "system",
                    "type_id": 1,
                },
            ]
        )

        m.post(
            self.cp.uri + "/activities/search",
            json=self.paginate_callback,
            headers={"filename": "activities_search.json"},
        )

        processed_blob = self.cp.get_activities()
        # No nested columns in Actvities
        blob_activities = processed_blob[0]["tbl"]

        assert_matching_tables(processed_activities, blob_activities)

    @requests_mock.Mocker()
    def test_get_custom_fields(self, m):
        m.get(
            self.cp.uri + "/custom_field_definitions/",
            json=self.paginate_callback,
            headers={"filename": "custom_fields_search.json"},
        )

        processed_blob = self.cp.get_custom_fields()
        self.assertTrue([f["name"] for f in processed_blob] == self.custom_field_table_names)
        for tbl in self.custom_field_table_names:
            assert_matching_tables(
                [f["tbl"] for f in processed_blob if f["name"] == tbl][0],
                self.custom_field_tables[tbl],
            )

    @requests_mock.Mocker()
    def test_get_activity_types(self, m):
        processed_at = Table(
            [
                {
                    "category": "system",
                    "count_as_interaction": False,
                    "id": 1,
                    "is_disabled": False,
                    "name": "Property Changed",
                },
                {
                    "category": "system",
                    "count_as_interaction": False,
                    "id": 3,
                    "is_disabled": False,
                    "name": "Pipeline Stage Changed",
                },
                {
                    "category": "user",
                    "count_as_interaction": False,
                    "id": 0,
                    "is_disabled": False,
                    "name": "Note",
                },
                {
                    "category": "user",
                    "count_as_interaction": True,
                    "id": 504464,
                    "is_disabled": False,
                    "name": "Mail",
                },
                {
                    "category": "user",
                    "count_as_interaction": True,
                    "id": 248465,
                    "is_disabled": False,
                    "name": "Stories from the Field",
                },
                {
                    "category": "user",
                    "count_as_interaction": True,
                    "id": 236962,
                    "is_disabled": False,
                    "name": "Press Coverage",
                },
            ]
        )

        m.get(
            self.cp.uri + "/activity_types/",
            json=self.paginate_callback,
            headers={"filename": "activity_types_list.json"},
        )

        processed_blob = self.cp.get_activity_types()
        # No nested columns in Activity Types
        blob_at = processed_blob[0]["tbl"]

        assert_matching_tables(processed_at, blob_at)

    @requests_mock.Mocker()
    def test_get_contact_types(self, m):
        processed_ct = Table(
            [
                {"id": 501947, "name": "Potential Customer"},
                {"id": 501948, "name": "Current Customer"},
                {"id": 501949, "name": "Uncategorized"},
                {"id": 501950, "name": "Group Leader"},
                {"id": 540331, "name": "Partner"},
                {"id": 540333, "name": "Funder"},
                {"id": 540334, "name": "Potential Funder"},
                {"id": 540335, "name": "Other"},
                {"id": 547508, "name": "Local Group"},
                {"id": 575833, "name": "Group Member"},
                {"id": 744795, "name": "Hill Contact"},
                {"id": 967249, "name": "State Leg Contact"},
            ]
        )

        m.get(
            self.cp.uri + "/contact_types/",
            json=self.paginate_callback,
            headers={"filename": "contact_types_list.json"},
        )

        processed_blob = self.cp.get_contact_types()
        assert_matching_tables(processed_ct, processed_blob)
