import json
import unittest

import requests_mock

from parsons import ActionBuilder, Table
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

        self.fake_field_values = {
            "Fake Field 2": "Fake Tag 5",
            self.fake_field_1: self.fake_tag_4,
        }

        self.fake_tagging = [
            {
                "action_builder:name": self.fake_tag_4,
                "action_builder:field": self.fake_field_1,
                "action_builder:section": self.fake_section,
            },
            {
                "action_builder:name": "Fake Tag 5",
                "action_builder:field": "Fake Field 2",
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

        self.fake_upsert_person = {
            "person": {
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
                    }
                ],
            }
        }

        self.fake_insert_person = {
            "entity_type": "Person",
            "data": {
                "person": {
                    "given_name": "Fakey",
                    "family_name": "McFakerson",
                    "email_addresses": [
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
        self.fake_update_person["identifier"] = [f"action_builder:{self.fake_entity_id}"]

        self.fake_tag_id = "fake_tag_id"
        self.fake_tagging_id = "fake_tagging_id"
        self.fake_remove_tag_resp = {"message": "Tag has been removed from Taggable Logbook"}

        # self.fake_connection = {"person_id": "fake-entity-id-2"}
        self.fake_connection = {
            "person_id": "fake-entity-id-2",
            "identifiers": ["action_builder:fake-connection-id"],
        }

    @requests_mock.Mocker()
    def test_get_page(self, m):
        m.get(
            f"{self.api_url}/tags?page=2&per_page=2",
            text=json.dumps(self.fake_tags_list_2),
        )
        self.assertEqual(self.bldr._get_page(self.campaign, "tags", 2, 2), self.fake_tags_list_2)

    @requests_mock.Mocker()
    def test_get_all_records(self, m):
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
            self.bldr._get_all_records(self.campaign, "tags"),
            Table(self.fake_tags_list),
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
        assert_matching_tables(self.bldr.get_campaign_tags(), Table(self.fake_tags_list))

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

    def prepare_dict_key_intersection(self, dict1, dict2):
        # Internal method to compare a reference dict to a new incoming one, keeping only common
        # keys whose values are not lists (i.e. nested).

        common_keys = {
            key for key, value in dict1.items() if key in dict2 and not isinstance(value, list)
        }

        dict1_comp = {key: value for key, value in dict1.items() if key in common_keys}

        dict2_comp = {key: value for key, value in dict2.items() if key in common_keys}

        return dict1_comp, dict2_comp

    @requests_mock.Mocker()
    def test_upsert_entity(self, m):
        m.post(f"{self.api_url}/people", text=json.dumps(self.fake_upserted_response))

        # Flatten and remove items added for spreadable arguments
        upsert_person = self.fake_upsert_person["person"]
        upsert_response = self.bldr._upsert_entity(self.fake_upsert_person, self.campaign)

        person_comp, upsert_response_comp = self.prepare_dict_key_intersection(
            upsert_person, upsert_response
        )

        upsert_email = upsert_person["email_addresses"][0]
        response_email = upsert_response["email_addresses"][0]

        email_comp, response_email_comp = self.prepare_dict_key_intersection(
            upsert_email, response_email
        )

        self.assertEqual(person_comp, upsert_response_comp)
        self.assertEqual(email_comp, response_email_comp)

    @requests_mock.Mocker()
    def test_insert_entity_record(self, m):
        m.post(f"{self.api_url}/people", text=json.dumps(self.fake_upserted_response))

        # Flatten and remove items added for spreadable arguments
        insert_person = {
            **{k: v for k, v in self.fake_insert_person.items() if k != "data"},
            **self.fake_insert_person["data"]["person"],
        }
        insert_response = self.bldr.insert_entity_record(**self.fake_insert_person)

        person_comp, insert_response_comp = self.prepare_dict_key_intersection(
            insert_person, insert_response
        )

        self.assertEqual(person_comp, insert_response_comp)

    @requests_mock.Mocker()
    def test_update_entity_record(self, m):
        m.post(f"{self.api_url}/people", text=json.dumps(self.fake_upserted_response))

        # Flatten and remove items added for spreadable arguments
        update_person = {
            **{k: v for k, v in self.fake_update_person.items() if k != "data"},
            **self.fake_update_person["data"]["person"],
        }
        update_response = self.bldr.update_entity_record(**self.fake_update_person)

        person_comp, update_response_comp = self.prepare_dict_key_intersection(
            update_person, update_response
        )

        self.assertEqual(person_comp, update_response_comp)

    @requests_mock.Mocker()
    def test_remove_entity_record_from_campaign(self, m):
        m.delete(
            f"{self.api_url}/people/{self.fake_entity_id}",
            json="{'message': 'Entity has been removed from the campaign'}",
        )

        remove_response = self.bldr.remove_entity_record_from_campaign(self.fake_entity_id)

        self.assertEqual(
            remove_response,
            "{'message': 'Entity has been removed from the campaign'}",
        )

    def tagging_callback(self, request, context):
        # Internal method for returning the constructed tag data to test

        post_data = request.json()
        tagging_data = post_data["add_tags"]

        # Force the sort to allow for predictable comparison
        return sorted(tagging_data, key=lambda k: k["action_builder:name"])

    @requests_mock.Mocker()
    def test_add_section_field_values_to_record(self, m):
        m.post(f"{self.api_url}/people", json=self.tagging_callback)
        add_tags_response = self.bldr.add_section_field_values_to_record(
            self.fake_entity_id, self.fake_section, self.fake_field_values
        )
        self.assertEqual(add_tags_response, self.fake_tagging)

    @requests_mock.Mocker()
    def test_remove_tagging(self, m):
        m.delete(
            f"{self.api_url}/tags/{self.fake_tag_id}/taggings/{self.fake_tagging_id}",
            json=self.fake_remove_tag_resp,
        )
        remove_tag_resp = self.bldr.remove_tagging(
            tag_id=self.fake_tag_id, tagging_id=self.fake_tagging_id
        )
        self.assertEqual(remove_tag_resp, self.fake_remove_tag_resp)

    def connect_callback(self, request, context):
        # Internal method for returning constructed connection data to test

        post_data = request.json()
        connection_data = post_data

        if request.method != "PUT":
            connection_data = post_data["connection"]

        url_pieces = [x for x in request.url.split("/") if x]

        # Grab ID if connections is penultimate in url path
        if url_pieces.index("connections") == len(url_pieces) - 2:
            connection_data["identifiers"] = [f"action_builder:{url_pieces[-1]}"]
        return connection_data

    @requests_mock.Mocker()
    def test_upsert_connection(self, m):
        m.post(
            f"{self.api_url}/people/{self.fake_entity_id}/connections",
            json=self.connect_callback,
        )
        connect_response = self.bldr.upsert_connection([self.fake_entity_id, "fake-entity-id-2"])
        self.assertEqual(
            connect_response,
            {
                **{k: v for k, v in self.fake_connection.items() if k != "identifiers"},
                **{"inactive": False},
            },
        )

    @requests_mock.Mocker()
    def test_deactivate_connection_post(self, m):
        m.post(
            f"{self.api_url}/people/{self.fake_entity_id}/connections",
            json=self.connect_callback,
        )
        connect_response = self.bldr.deactivate_connection(
            self.fake_entity_id, to_identifier="fake-entity-id-2"
        )
        self.assertEqual(
            connect_response,
            {
                **{k: v for k, v in self.fake_connection.items() if k != "identifiers"},
                **{"inactive": True},
            },
        )

    @requests_mock.Mocker()
    def test_deactivate_connection_put(self, m):
        conn_endpoint = f"{self.api_url}/people/{self.fake_entity_id}/connections"
        conn_endpoint += "/fake-connection-id"
        m.put(
            conn_endpoint,
            json=self.connect_callback,
        )
        connect_response = self.bldr.deactivate_connection(
            self.fake_entity_id, connection_identifier="fake-connection-id"
        )
        self.assertEqual(
            connect_response,
            {
                **{k: v for k, v in self.fake_connection.items() if k != "person_id"},
                **{"inactive": True},
            },
        )
