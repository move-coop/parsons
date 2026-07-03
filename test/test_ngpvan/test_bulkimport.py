from parsons import VAN, Table
from parsons.utilities import cloud_storage
from test.conftest import assert_matching_tables


def test_get_bulk_import_resources(van: VAN, requests_mock):
    json = ["Contacts", "Contributions", "ActivistCodes", "ContactsActivistCodes"]

    requests_mock.get(van.connection.uri + "bulkImportJobs/resources", json=json)

    assert van.get_bulk_import_resources() == json


def test_get_bulk_import_job(van: VAN, requests_mock):
    requests_mock.get(van.connection.uri + "bulkImportJobs/53407", json=bulk_import_job)

    assert van.get_bulk_import_job(53407) == bulk_import_job


def test_get_bulk_import_job_results(van: VAN, requests_mock):
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

    requests_mock.get(van.connection.uri + "bulkImportJobs/53407", json=bulk_import_job)
    assert_matching_tables(van.get_bulk_import_job_results(53407), results_tbl)


def test_get_bulk_import_mapping_types(van: VAN, requests_mock):
    requests_mock.get(van.connection.uri + "bulkImportMappingTypes", json=[mapping_type])

    assert_matching_tables(van.get_bulk_import_mapping_types(), Table([mapping_type]))


def test_get_bulk_import_mapping_type(van: VAN, requests_mock):
    requests_mock.get(
        van.connection.uri + "bulkImportMappingTypes/ActivistCode",
        json=mapping_type,
    )

    assert van.get_bulk_import_mapping_type("ActivistCode") == mapping_type


def get_bulk_import_mapping_type_fields(van: VAN, requests_mock):
    json = [
        {"name": "Unsubscribed", "id": "0", "parents": None},
        {"name": "Not Subscribed", "id": "1", "parents": None},
        {"name": "Subscribed", "id": "2", "parents": None},
    ]
    requests_mock.get(
        van.connection.uri + "bulkImportMappingTypes/Email/EmailSubscriptionStatusId/values"
    )

    r = van.get_bulk_import_mapping_type_fields("Email", "EmailSubscriptionStatusId")
    assert json == r


def test_post_bulk_import(van: VAN, requests_mock, mocker):
    # Mock Cloud Storage
    post_file = mocker.patch.object(cloud_storage, "post_file")
    post_file.return_value = "https://s3.com/my_file.zip"

    tbl = Table([["Vanid", "ActivistCodeID"], [1234, 345345]])

    requests_mock.post(van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

    r = van.post_bulk_import(
        tbl,
        "S3",
        "ContactsActivistCodes",
        [{"name": "ActivistCode"}],
        "Activist Code Upload",
        bucket="my-bucket",
    )

    assert r == 54679


def test_bulk_apply_activist_codes(van: VAN, requests_mock, mocker):
    # Mock Cloud Storage
    post_file = mocker.patch.object(cloud_storage, "post_file")
    post_file.return_value = "https://s3.com/my_file.zip"

    tbl = Table([["Vanid", "ActivistCodeID"], [1234, 345345]])

    requests_mock.post(van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

    job_id = van.bulk_apply_activist_codes(tbl, url_type="S3", bucket="my-bucket")

    assert job_id == 54679


def test_bulk_apply_suppressions(van: VAN, requests_mock, mocker):
    # Mock Cloud Storage
    post_file = mocker.patch.object(cloud_storage, "post_file")
    post_file.return_value = "https://s3.com/my_file.zip"

    tbl = Table([["Vanid", "suppressionid"], [1234, 18]])

    requests_mock.post(van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

    job_id = van.bulk_apply_suppressions(tbl, url_type="S3", bucket="my-bucket")

    assert job_id == 54679


def test_bulk_upsert_contacts(van: VAN, requests_mock, mocker):
    # Mock Cloud Storage
    post_file = mocker.patch.object(cloud_storage, "post_file")
    post_file.return_value = "https://s3.com/my_file.zip"

    tbl = Table([["Vanid", "email"], [1234, "me@me.com"]])

    requests_mock.post(van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

    job_id = van.bulk_upsert_contacts(tbl, url_type="S3", bucket="my-bucket")

    assert job_id == 54679


def test_bulk_apply_canvass_results(van: VAN, requests_mock, mocker):
    # Mock Cloud Storage
    post_file = mocker.patch.object(cloud_storage, "post_file")
    post_file.return_value = "https://s3.com/my_file.zip"

    tbl = Table(
        [
            ["vanid", "contacttypeid", "resultid", "datecanvassed", "canvassedby", "phone"],
            [1234, 1, 1, "2020-01-01", 987, "5554443210"],
        ]
    )

    requests_mock.post(van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

    job_id = van.bulk_apply_canvass_results(tbl, url_type="S3", bucket="my-bucket")

    assert job_id == 54679


def test_bulk_apply_contact_custom_fields(van: VAN, requests_mock, mocker):
    # Mock Cloud Storage
    post_file = mocker.patch.object(cloud_storage, "post_file")
    post_file.return_value = "https://s3.com/my_file.zip"

    tbl = Table([["vanid", "CF123", "CF124"], [1234, "Test String Value", 999]])

    requests_mock.post(van.connection.uri + "bulkImportJobs", json={"jobId": 54679})

    custom_field_group_id = 1234

    job_id = van.bulk_apply_contact_custom_fields(
        custom_field_group_id, tbl, url_type="S3", bucket="my-bucket"
    )

    assert job_id == 54679


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
