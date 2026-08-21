from pathlib import Path

import pytest
from google.cloud import storage

from parsons import GoogleCloudStorage, Table
from parsons.utilities import files
from test.conftest import assert_matching_tables

TEMP_BUCKET_NAME = "parsons_test"
TEMP_FILE_NAME = "tmp_file_01.txt"


@pytest.fixture
def cloud():
    """Provide a live GoogleCloudStorage connector with a temp bucket and file."""
    cloud = GoogleCloudStorage()

    # Running into some issues creating and delete too many buckets, so
    # will check to see if it already exists
    if not cloud.bucket_exists(TEMP_BUCKET_NAME):
        cloud.create_bucket(TEMP_BUCKET_NAME)

        # Upload a file
        tmp_file_path = files.string_to_temp_file("A little string", suffix=".txt")
        cloud.put_blob(TEMP_BUCKET_NAME, TEMP_FILE_NAME, tmp_file_path)

    return cloud


@pytest.mark.live
def test_list_buckets(cloud):
    # Assert that it finds the correct buckets
    bucket_list = cloud.list_buckets()

    # Make sure that my bucket is in the list
    assert TEMP_BUCKET_NAME in bucket_list


@pytest.mark.live
def test_bucket_exists(cloud):
    # Assert finds a bucket that exists
    assert cloud.bucket_exists(TEMP_BUCKET_NAME)

    # Assert doesn't find a bucket that doesn't exist
    assert not cloud.bucket_exists("NOT_A_REAL_BUCKET")


@pytest.mark.live
def test_get_bucket(cloud):
    # Assert that a bucket object is returned
    assert isinstance(cloud.get_bucket(TEMP_BUCKET_NAME), storage.bucket.Bucket)


@pytest.mark.live
def test_create_bucket(cloud):
    # Temporary bucket has already been created as part of set up, so just checking
    # that it really exists
    assert cloud.bucket_exists(TEMP_BUCKET_NAME)


@pytest.mark.live
def test_delete_bucket(cloud):
    # Create another bucket, delete it and make sure it doesn't exist
    cloud.create_bucket(TEMP_BUCKET_NAME + "_2")
    cloud.delete_bucket(TEMP_BUCKET_NAME + "_2")
    assert not cloud.bucket_exists(TEMP_BUCKET_NAME + "_2")


@pytest.mark.live
def test_list_blobs(cloud):
    blob_list = cloud.list_blobs(TEMP_BUCKET_NAME)

    # Make sure that my file is in the list
    assert TEMP_FILE_NAME in blob_list

    # Make sure that there is only one file in the bucket
    assert len(blob_list) == 1


@pytest.mark.live
def test_blob_exists(cloud):
    # Assert that it thinks that the blob exists
    assert cloud.blob_exists(TEMP_BUCKET_NAME, TEMP_FILE_NAME)

    # Assert that it thinks that a non-existent blob doesn't exist
    assert not cloud.blob_exists(TEMP_BUCKET_NAME, "FAKE_BLOB")


@pytest.mark.live
def test_put_blob(cloud):
    # Already being tested as part of the cloud fixture
    pass


@pytest.mark.live
def test_get_blob(cloud):
    # Assert that a blob object is returned
    assert isinstance(cloud.get_blob(TEMP_BUCKET_NAME, TEMP_FILE_NAME), storage.blob.Blob)


@pytest.mark.live
def test_download_blob(cloud):
    # Download blob and ensure that it is the expected file
    blob = Path(cloud.download_blob(TEMP_BUCKET_NAME, TEMP_FILE_NAME))
    assert blob.read_text() == "A little string"


@pytest.mark.live
def test_delete_blob(cloud):
    file_name = "delete_me.txt"

    # Upload a file
    tmp_file_path = files.string_to_temp_file("A little string", suffix=".txt")
    cloud.put_blob(TEMP_BUCKET_NAME, file_name, tmp_file_path)

    # Check that it was deleted.
    cloud.delete_blob(TEMP_BUCKET_NAME, file_name)
    assert not cloud.blob_exists(TEMP_BUCKET_NAME, file_name)


@pytest.mark.live
def test_get_url(cloud):
    file_name = "delete_me.csv"
    input_tbl = Table([["a"], ["1"]])
    cloud.upload_table(input_tbl, TEMP_BUCKET_NAME, file_name)
    url = cloud.get_url(TEMP_BUCKET_NAME, file_name)
    download_tbl = Table.from_csv(url)
    assert_matching_tables(input_tbl, download_tbl)
