import os
import unittest

import requests_mock
from airtable_responses import (
    delete_responses,
    insert_response,
    insert_responses,
    records_response,
    records_response_with_more_columns,
    update_responses,
    upsert_with_id_responses,
    upsert_with_key_responses,
)

from parsons import Airtable, Table
from test.utils import assert_matching_tables

os.environ["AIRTABLE_PERSONAL_ACCESS_TOKEN"] = "SOME_TOKEN"
BASE_KEY = "BASEKEY"
TABLE_NAME = "TABLENAME"


class TestAirtable(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        self.base_uri = f"https://api.airtable.com/v0/{BASE_KEY}/{TABLE_NAME}"

        m.get(self.base_uri, status_code=200)

        self.at = Airtable(base_key=BASE_KEY, table_name=TABLE_NAME)

    @requests_mock.Mocker()
    def test_get_record(self, m):
        record_id = "recObtmLUrD5dOnmD"

        response = {
            "id": record_id,
            "fields": {},
            "createdTime": "2019-05-08T19:37:58.000Z",
        }
        m.get(self.base_uri + "/" + record_id, json=response)

        # Assert the method returns expected dict response
        self.assertEqual(self.at.get_record(record_id), response)

    @requests_mock.Mocker()
    def test_get_records(self, m):
        m.get(self.base_uri, json=records_response)

        tbl = Table(
            [
                {
                    "id": "recaBMSHTgXREa5ef",
                    "createdTime": "2019-05-08T19:37:58.000Z",
                    "Name": "This is a row!",
                },
                {
                    "id": "recObtmLUrD5dOnmD",
                    "createdTime": "2019-05-08T19:37:58.000Z",
                    "Name": None,
                },
                {
                    "id": "recmeBNnj4cuHPOSI",
                    "createdTime": "2019-05-08T19:37:58.000Z",
                    "Name": None,
                },
            ]
        )

        self.at.get_records(max_records=1)
        # Assert that Parsons tables match
        assert_matching_tables(self.at.get_records(), tbl)

    @requests_mock.Mocker()
    def test_get_records_with_1_sample(self, m):
        m.get(self.base_uri, json=records_response_with_more_columns)

        airtable_res = self.at.get_records(sample_size=1)

        assert airtable_res.columns == ["id", "createdTime", "Name"]

    @requests_mock.Mocker()
    def test_get_records_with_5_sample(self, m):
        m.get(self.base_uri, json=records_response_with_more_columns)

        airtable_res = self.at.get_records(sample_size=5)

        assert airtable_res.columns == ["id", "createdTime", "Name", "SecondColumn"]

    @requests_mock.Mocker()
    def test_get_records_with_explicit_headers(self, m):
        m.get(self.base_uri, json=records_response_with_more_columns)

        fields = ["Name", "SecondColumn"]

        airtable_res = self.at.get_records(fields, sample_size=1)

        assert airtable_res.columns == ["id", "createdTime", "Name", "SecondColumn"]

    @requests_mock.Mocker()
    def test_get_records_with_single_field(self, m):
        m.get(self.base_uri, json=records_response_with_more_columns)

        fields = "Name"

        airtable_res = self.at.get_records(fields, sample_size=1)

        assert airtable_res.columns == ["id", "createdTime", "Name"]

    @requests_mock.Mocker()
    def test_insert_record(self, m):
        m.post(self.base_uri, json=insert_response)

        resp = self.at.insert_record({"Name": "Another row!"})

        # Assert that returned dict conforms to expected.
        self.assertEqual(resp, insert_response)

    @requests_mock.Mocker()
    def test_insert_records(self, m):
        m.post(self.base_uri, json=insert_responses)

        tbl = Table([{"Name": "Another row!"}, {"Name": "Another!"}])
        resp = self.at.insert_records(tbl)

        # Assert that row count is expected
        self.assertEqual(len(resp), 2)

    @requests_mock.Mocker()
    def test_update_record(self, m):
        record_id = "recObtmLUrD5dOnmD"

        update_response = {
            "id": record_id,
            "fields": {"Name": "AName"},
            "createdTime": "2023-05-22T21:24:15.333134Z",
        }

        m.patch(self.base_uri + "/" + record_id, json=update_response)

        # Assert the method returns expected dict response
        self.assertEqual(self.at.update_record(record_id, {"Name": "AName"}), update_response)

    @requests_mock.Mocker()
    def test_update_records(self, m):
        m.patch(self.base_uri, json=update_responses)

        tbl = Table(
            [
                {"id": "recaBMSHTgXREa5ef", "Name": "Updated Name1"},
                {"id": "recObtmLUrD5dOnmD", "Name": "Updated Name2"},
                {"id": "recmeBNnj4cuHPOSI", "Name": "Updated Name3"},
            ]
        )

        resp = self.at.update_records(tbl)

        self.assertTrue(len(update_responses["records"]), len(resp))

    @requests_mock.Mocker()
    def test_upsert_records_with_id(self, m):
        m.patch(self.base_uri, json=upsert_with_id_responses)

        tbl = Table(
            [
                {"id": "recz9W2ojGNwMdN2y", "Name": "Updated Name1"},
                {"id": "recB5njCET7AvHBbg", "Name": "Updated Name2"},
                {"id": "recz9W2ojgPwMdN2y", "Name": "New Name3"},
            ]
        )

        resp = self.at.upsert_records(tbl)

        self.assertTrue(len(upsert_with_id_responses["records"]), len(resp))
        self.assertTrue(len(resp["updated_records"]), 2)
        self.assertTrue(len(resp["created_records"]), 1)

    @requests_mock.Mocker()
    def test_upsert_records_with_key(self, m):
        m.patch(self.base_uri, json=upsert_with_key_responses)

        tbl = Table(
            [
                {"key": "1", "Name": "New Name1"},
                {"key": "2", "Name": "New Name2"},
                {"key": "3", "Name": "Updated Name3"},
            ]
        )

        resp = self.at.upsert_records(tbl, key_fields=["key"])

        self.assertTrue(len(upsert_with_key_responses["records"]), len(resp))
        self.assertTrue(len(resp["updated_records"]), 1)
        self.assertTrue(len(resp["created_records"]), 2)

    @requests_mock.Mocker()
    def test_delete_record(self, m):
        record_id = "recObtmLUrD5dOnmD"

        response = {
            "id": record_id,
            "deleted": True,
        }

        m.delete(self.base_uri + "/" + record_id, json=response)

        # Assert the method returns expected dict response
        self.assertEqual(
            self.at.delete_record(record_id),
            response,
        )

    @requests_mock.Mocker()
    def test_delete_records(self, m):
        m.delete(self.base_uri, json=delete_responses)

        tbl = Table(delete_responses["records"]).cut("id")

        resp = self.at.delete_records(tbl)

        self.assertEqual(len(delete_responses["records"]), len(resp))
        self.assertTrue(all(r["deleted"] for r in resp))
