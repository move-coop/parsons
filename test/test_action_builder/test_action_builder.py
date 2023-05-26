import unittest
import requests_mock
import json
from parsons import Table, ActionBuilder
from test.utils import assert_matching_tables


class TestActionBuilder(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        self.subdomain = "fake_subdomain"
        self.campaign = "fake-campaign"
        self.api_url = "https://{}.actionbuilder.org/api/rest/v1/campaigns/{}".format(
            self.subdomain, self.campaign
        )
        self.api_key = "fake_key"

        self.bldr = ActionBuilder(
            api_token=self.api_key, subdomain=self.subdomain, campaign=self.campaign
        )

        self.fake_datetime = "2023-05-19T00:00:00.000Z"
        self.fake_date = "2023-05-19"

        self.fake_tag_1 = "Fake Tag 1"
        self.fake_tag_2 = "Fake Tag 2"
        self.fake_tag_3 = "Fake Tag 3"
        self.fake_tag_4 = "Fake Tag 3"

        self.fake_field_1 = "Fake Field 1"
        self.fake_section = "Fake Section 1"

        self.fake_tags_list_1 = {
            "per_page": 2,
            "page": 1,
            "total_pages": 9,
            "_embedded": {
                "osdi:tags": [
                    {
                        "origin_system": "Action Builder",
                        "identifiers": ["action_builder:fake-action-builder-id-1"],
                        "created_date": self.fake_datetime,
                        "modified_date": self.fake_datetime,
                        "name": self.fake_tag_1,
                        "action_builder:section": self.fake_section,
                        "action_builder:field": self.fake_field_1,
                        "action_builder:field_type": "standard",
                        "action_builder:locked": False,
                        "action_builder:allow_multiple_responses": False,
                    },
                    {
                        "origin_system": "Action Builder",
                        "identifiers": ["action_builder:fake-action-builder-id-2"],
                        "created_date": self.fake_datetime,
                        "modified_date": self.fake_datetime,
                        "name": self.fake_tag_2,
                        "action_builder:section": self.fake_section,
                        "action_builder:field": self.fake_field_1,
                        "action_builder:field_type": "standard",
                        "action_builder:locked": False,
                        "action_builder:allow_multiple_responses": False,
                    },
                ]
            },
        }

        self.fake_tag_name_search_result = {
            "per_page": 1,
            "page": 1,
            "total_pages": 1,
            "_embedded": {
                "osdi:tags": [
                    {
                        "origin_system": "Action Builder",
                        "identifiers": ["action_builder:fake-action-builder-id-1"],
                        "created_date": self.fake_datetime,
                        "modified_date": self.fake_datetime,
                        "name": self.fake_tag_1,
                        "action_builder:section": self.fake_section,
                        "action_builder:field": self.fake_field_1,
                        "action_builder:field_type": "standard",
                        "action_builder:locked": False,
                        "action_builder:allow_multiple_responses": False,
                    }
                ]
            },
        }

        self.fake_tags_list_2 = {
            "per_page": 2,
            "page": 2,
            "total_pages": 9,
            "_embedded": {
                "osdi:tags": [
                    {
                        "origin_system": "Action Builder",
                        "identifiers": ["action_builder:fake-action-builder-id-3"],
                        "created_date": self.fake_datetime,
                        "modified_date": self.fake_datetime,
                        "name": self.fake_tag_3,
                        "action_builder:section": self.fake_section,
                        "action_builder:field": self.fake_field_1,
                        "action_builder:field_type": "standard",
                        "action_builder:locked": False,
                        "action_builder:allow_multiple_responses": False,
                    },
                    {
                        "origin_system": "Action Builder",
                        "identifiers": ["action_builder:fake-action-builder-id-4"],
                        "created_date": self.fake_datetime,
                        "modified_date": self.fake_datetime,
                        "name": self.fake_tag_4,
                        "action_builder:section": self.fake_section,
                        "action_builder:field": self.fake_field_1,
                        "action_builder:field_type": "standard",
                        "action_builder:locked": False,
                        "action_builder:allow_multiple_responses": False,
                    },
                ]
            },
        }

        self.fake_tags_list = (
            self.fake_tags_list_1["_embedded"]["osdi:tags"]
            + self.fake_tags_list_2["_embedded"]["osdi:tags"]
        )

        self.fake_tag_names = [
            "Fake Tag 5",
            self.fake_tag_4,
            self.fake_tag_3,
            self.fake_tag_2,
        ]
        self.fake_tag_fields = ["Fake Field 2", self.fake_field_1]

        self.fake_tagging = [
            {
                "action_builder:name": "Fake Tag 5",
                "action_builder:field": "Fake Field 2",
                "action_builder:section": self.fake_section,
            },
            {
                "action_builder:name": self.fake_tag_4,
                "action_builder:field": self.fake_field_1,
                "action_builder:section": self.fake_section,
            },
            {
                "action_builder:name": self.fake_tag_3,
                "action_builder:field": self.fake_field_1,
                "action_builder:section": self.fake_section,
            },
            {
                "action_builder:name": self.fake_tag_2,
                "action_builder:field": self.fake_field_1,
                "action_builder:section": self.fake_section,
            },
        ]

        self.fake_entity_id = "fake-entity-id-1"

        self.fake_upserted_response = {
            "origin_system": "Action Builder",
            "identifiers": [f"action_builder:{self.fake_entity_id}"],
            "created_date": self.fake_datetime,
            "modified_date": self.fake_datetime,
            "action_builder:entity_type": "Person",
            "given_name": "Fakey",
            "family_name": "McFakerson",
            "preferred_language": "en",
            "email_addresses": [
                {
                    "action_builder:identifier": "action_builder:fake-email-id-1",
                    "address": "fakey@mcfakerson.com",
                    "address_type": "Work",
                    "status": "unsubscribed",
                    "source": "api",
                }
            ],
        }

        self.fake_insert_person = {
            "entity_type": "Person",
            "data": {
                "person": {
                    "given_name": "Fakey",
                    "family_name": "McFakerson",
                    "email_address": [
                        {"address": "fakey@mcfakerson.com", "status": "unsubscribed"}
                    ],
                    "created_date": self.fake_datetime,
                    "modified_date": self.fake_datetime,
                }
            },
        }

        self.fake_update_person = {
            k: v for k, v in self.fake_insert_person.items() if k != "entity_type"
        }
        self.fake_update_person["identifiers"] = [
            f"action_builder:{self.fake_entity_id}"
        ]

        self.fake_connection = {"person_id": "fake-entity-id-2"}

    @requests_mock.Mocker()
    def test_get_page(self, m):
        m.get(
            f"{self.api_url}/tags?page=2&per_page=2",
            text=json.dumps(self.fake_tags_list_2),
        )
        self.assertEqual(
            self.bldr._get_page(self.campaign, "tags", 2, 2), self.fake_tags_list_2
        )

    @requests_mock.Mocker()
    def test_get_entry_list(self, m):
        m.get(
            f"{self.api_url}/tags?page=1&per_page=25",
            text=json.dumps(self.fake_tags_list_1),
        )
        m.get(
            f"{self.api_url}/tags?page=2&per_page=25",
            text=json.dumps(self.fake_tags_list_2),
        )
        m.get(
            f"{self.api_url}/tags?page=3&per_page=25",
            text=json.dumps({"_embedded": {"osdi:tags": []}}),
        )
        assert_matching_tables(
            self.bldr._get_entry_list(self.campaign, "tags"), Table(self.fake_tags_list)
        )

    @requests_mock.Mocker()
    def test_get_campaign_tags(self, m):
        m.get(
            f"{self.api_url}/tags?page=1&per_page=25",
            text=json.dumps(self.fake_tags_list_1),
        )
        m.get(
            f"{self.api_url}/tags?page=2&per_page=25",
            text=json.dumps(self.fake_tags_list_2),
        )
        m.get(
            f"{self.api_url}/tags?page=3&per_page=25",
            text=json.dumps({"_embedded": {"osdi:tags": []}}),
        )
        assert_matching_tables(
            self.bldr.get_campaign_tags(), Table(self.fake_tags_list)
        )

    @requests_mock.Mocker()
    def test_get_tag_by_name(self, m):
        m.get(
            f"{self.api_url}/tags?filter=name eq '{self.fake_tag_1}'",
            text=json.dumps(self.fake_tag_name_search_result),
        )
        m.get(
            f"{self.api_url}/tags?page=2&per_page=25&filter=name eq '{self.fake_tag_1}'",
            text=json.dumps({"_embedded": {"osdi:tags": []}}),
        )
        assert_matching_tables(
            self.bldr.get_tag_by_name(self.fake_tag_1),
            Table([self.fake_tags_list_1["_embedded"]["osdi:tags"][0]]),
        )

    def compare_to_incoming(self, dict1, dict2):
        # Internal method to compare a reference dict to a new incoming one, keeping only common
        # keys (or where incoming key is substring). Recursive to handle nesting/JSON.

        incoming = {[key for key in dict1 if k in key][0]: v for k, v in dict2.items()}
        compare = {k: v for k, v in dict1.items() if k in incoming}

        for key, val in incoming.items():
            print(key)
            if isinstance(val, dict):
                insub, compsub = self.compare_to_incoming(compare[key], val)
                incoming[key] = insub
                compare[key] = compsub
            elif isinstance(val, list) and isinstance(val[0], dict):
                for i in range(len(val)):
                    print(i)
                    insub, compsub = self.compare_to_incoming(compare[key][i], val[i])
                    incoming[key][i] = insub
                    compare[key][i] = compsub

        return incoming, compare

    @requests_mock.Mocker()
    def test_upsert_entity(self, m):
        m.post(f"{self.api_url}/people", text=json.dumps(self.fake_upserted_response))

        # Flatten and remove items added for spreadable arguments
        insert_flattened = {
            **{k: v for k, v in self.fake_insert_person.items() if k != "data"},
            **self.fake_insert_person["data"]["person"],
        }
        insert_incoming, insert_compare = self.compare_to_incoming(
            self.bldr.upsert_entity(**self.fake_insert_person), insert_flattened
        )

        update_flattened = {
            **{k: v for k, v in self.fake_update_person.items() if k != "data"},
            **self.fake_update_person["data"]["person"],
        }
        update_incoming, update_compare = self.compare_to_incoming(
            self.bldr.upsert_entity(**self.fake_update_person), update_flattened
        )
        self.assertEqual(insert_incoming, insert_compare)
        self.assertEqual(update_incoming, update_compare)

    def tagging_callback(self, request, context):
        # Internal method for returning the constructed tag data to test

        post_data = request.json()
        tagging_data = post_data["add_tags"]
        return tagging_data

    @requests_mock.Mocker()
    def test_add_tags_to_record(self, m):
        m.post(f"{self.api_url}/people", json=self.tagging_callback)
        add_tags_response = self.bldr.add_tags_to_record(
            self.fake_entity_id,
            self.fake_tag_names,
            self.fake_tag_fields,
            self.fake_section,
        )
        self.assertEqual(add_tags_response, self.fake_tagging)

    def connect_callback(self, request, context):
        # Internal method for returning constructed connection data to test

        post_data = request.json()
        connection_data = post_data["connection"]
        return connection_data

    @requests_mock.Mocker()
    def test_upsert_connection(self, m):
        m.post(
            f"{self.api_url}/people/{self.fake_entity_id}/connections",
            json=self.connect_callback,
        )
        connect_response = self.bldr.upsert_connection(
            [self.fake_entity_id, "fake-entity-id-2"]
        )
        self.assertEqual(connect_response, self.fake_connection)
