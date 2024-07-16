import unittest
import os
import requests_mock
import unittest.mock as mock
from parsons import VAN, Table
from test.utils import assert_matching_tables
from parsons.utilities import cloud_storage

os.environ["VAN_API_KEY"] = "SOME_KEY"


class TestBulkImport(unittest.TestCase):
    def setUp(self):

        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters", raise_for_status=False)

    @requests_mock.Mocker()
    def test_get_bulk_import_resources(self, m):

        json = ["Contacts", "Contributions", "ActivistCodes", "ContactsActivistCodes"]

        m.get(self.van.connection.uri + "bulkImportJobs/resources", json=json)

        self.assertEqual(self.van.get_bulk_import_resources(), json)

    @requests_mock.Mocker()
    def test_get_bulk_import_job(self, m):

        m.get(self.van.connection.uri + "bulkImportJobs/53407", json=bulk_import_job)

        self.assertEqual(self.van.get_bulk_import_job(53407), bulk_import_job)

    @requests_mock.Mocker()
    def test_get_bulk_import_job_results(self, m):

        results_tbl = Table(
            [
                [
                    "BulkUploadDataID",
                    "ULFileID",
                    "PrimaryKey",
                    "PrimaryKeyType",
                    "MailingAddress_3581",
                ],
                ["1", "1983", "101596008", "VanID", "Processed"],
            ]
        )

        bulk_import_job = {
            "id": 92,
            "status": "Completed",
            "resourceType": "Contacts",
            "webhookUrl": None,
            "resultFileSizeLimitKb": 5000,
            "errors": [],
            "resultFiles": [
                {
                    "url": Table.to_csv(results_tbl),
                    "dateExpired": "2020-09-04T22:07:04.0770295-04:00",
                }
            ],
        }

        m.get(self.van.connection.uri + "bulkImportJobs/53407", json=bulk_import_job)
        assert_matching_tables(self.van.get_bulk_import_job_results(53407), results_tbl)

    @requests_mock.Mocker()
    def test_get_bulk_import_mapping_types(self, m):

        m.get(self.van.connection.uri + "bulkImportMappingTypes", json=[mapping_type])

        assert_matching_tables(self.van.get_bulk_import_mapping_types(), Table([mapping_type]))

    @requests_mock.Mocker()
    def test_get_bulk_import_mapping_type(self, m):

        m.get(
            self.van.connection.uri + "bulkImportMappingTypes/ActivistCode",
            json=mapping_type,
        )

        self.assertEqual(self.van.get_bulk_import_mapping_type("ActivistCode"), mapping_type)

    @requests_mock.Mocker()
    def get_bulk_import_mapping_type_fields(self, m):

        json = [
            {"name": "Unsubscribed", "id": "0", "parents": None},
            {"name": "Not Subscribed", "id": "1", "parents": None},
            {"name": "Subscribed", "id": "2", "parents": None},
        ]
        m.get(
            self.van.connection.uri
            + "bulkImportMappingTypes/Email/EmailSubscriptionStatusId/values"
        )

        r = self.van.get_bulk_import_mapping_type_fields("Email", "EmailSubscriptionStatusId")
        self.assertEqual(json, r)

    @requests_mock.Mocker()
    def test_post_bulk_import(self, m):

        # Mock Cloud Storage
        cloud_storage.post_file = mock.MagicMock()
        cloud_storage.post_file.return_value = "https://s3.com/my_file.zip"

        tbl = Table([["Vanid", "ActivistCodeID"], [1234, 345345]])

        m.post(self.van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

        r = self.van.post_bulk_import(
            tbl,
            "S3",
            "ContactsActivistCodes",
            [{"name": "ActivistCode"}],
            "Activist Code Upload",
            bucket="my-bucket",
        )

        self.assertEqual(r, 54679)

    @requests_mock.Mocker()
    def test_bulk_apply_activist_codes(self, m):

        # Mock Cloud Storage
        cloud_storage.post_file = mock.MagicMock()
        cloud_storage.post_file.return_value = "https://s3.com/my_file.zip"

        tbl = Table([["Vanid", "ActivistCodeID"], [1234, 345345]])

        m.post(self.van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

        job_id = self.van.bulk_apply_activist_codes(tbl, url_type="S3", bucket="my-bucket")

        self.assertEqual(job_id, 54679)

    @requests_mock.Mocker()
    def test_bulk_apply_suppressions(self, m):

        # Mock Cloud Storage
        cloud_storage.post_file = mock.MagicMock()
        cloud_storage.post_file.return_value = "https://s3.com/my_file.zip"

        tbl = Table([["Vanid", "suppressionid"], [1234, 18]])

        m.post(self.van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

        job_id = self.van.bulk_apply_suppressions(tbl, url_type="S3", bucket="my-bucket")

        self.assertEqual(job_id, 54679)

    @requests_mock.Mocker()
    def test_bulk_upsert_contacts(self, m):

        # Mock Cloud Storage
        cloud_storage.post_file = mock.MagicMock()
        cloud_storage.post_file.return_value = "https://s3.com/my_file.zip"

        tbl = Table([["Vanid", "email"], [1234, "me@me.com"]])

        m.post(self.van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

        job_id = self.van.bulk_upsert_contacts(tbl, url_type="S3", bucket="my-bucket")

        self.assertEqual(job_id, 54679)

    @requests_mock.Mocker()
    def test_bulk_apply_canvass_results(self, m):

        # Mock Cloud Storage
        cloud_storage.post_file = mock.MagicMock()
        cloud_storage.post_file.return_value = "https://s3.com/my_file.zip"

        tbl = Table(
            [
                ["vanid", "contacttypeid", "resultid", "datecanvassed", "canvassedby", "phone"],
                [1234, 1, 1, "2020-01-01", 987, "5554443210"],
            ]
        )

        m.post(self.van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

        job_id = self.van.bulk_apply_canvass_results(tbl, url_type="S3", bucket="my-bucket")

        self.assertEqual(job_id, 54679)

    @requests_mock.Mocker()
    def test_bulk_apply_contact_custom_fields(self, m):

        # Mock Cloud Storage
        cloud_storage.post_file = mock.MagicMock()
        cloud_storage.post_file.return_value = "https://s3.com/my_file.zip"

        tbl = Table([["vanid", "CF123", "CF124"], [1234, "Test String Value", 999]])

        m.post(self.van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

        custom_field_group_id = 1234

        job_id = self.van.bulk_apply_contact_custom_fields(
            custom_field_group_id, tbl, url_type="S3", bucket="my-bucket"
        )

        self.assertEqual(job_id, 54679)


mapping_type = {
    "name": "ActivistCode",
    "displayName": "Apply Activist Code",
    "allowMultipleMode": "Multiple",
    "resourceTypes": ["Contacts", "ContactsActivistCodes"],
    "fields": [
        {
            "name": "ActivistCodeID",
            "description": "Activist Code ID",
            "hasPredefinedValues": True,
            "isRequired": True,
            "canBeMappedToColumn": True,
            "canBeMappedByName": True,
            "parents": None,
        },
        {
            "name": "CanvassedBy",
            "description": "Recruited By, Must be a Valid User ID",
            "hasPredefinedValues": False,
            "isRequired": False,
            "canBeMappedToColumn": True,
            "canBeMappedByName": True,
            "parents": None,
        },
        {
            "name": "DateCanvassed",
            "description": "Contacted When",
            "hasPredefinedValues": False,
            "isRequired": False,
            "canBeMappedToColumn": True,
            "canBeMappedByName": True,
            "parents": [{"parentFieldName": "CanvassedBy", "limitedToParentValues": None}],
        },
        {
            "name": "ContactTypeID",
            "description": "Contacted How",
            "hasPredefinedValues": True,
            "isRequired": False,
            "canBeMappedToColumn": True,
            "canBeMappedByName": True,
            "parents": [{"parentFieldName": "CanvassedBy", "limitedToParentValues": None}],
        },
    ],
}

bulk_import_job = {
    "id": 92,
    "status": "Completed",
    "resourceType": "Contacts",
    "webhookUrl": None,
    "resultFileSizeLimitKb": 5000,
    "errors": [],
    "resultFiles": [
        {
            "url": "https://ngpvan.com/bulk-import-jobs/f023.csv",
            "dateExpired": "2020-09-04T22:07:04.0770295-04:00",
        }
    ],
}
