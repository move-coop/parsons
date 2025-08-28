import os
import unittest

from google.cloud import storage

from parsons import GoogleCloudStorage, Table
from parsons.utilities import files
from test.utils import assert_matching_tables

TEMP_BUCKET_NAME = "parsons_test"
TEMP_FILE_NAME = "tmp_file_01.txt"


@unittest.skipIf(not os.environ.get("LIVE_TEST"), "Skipping because not running live test")
class TestGoogleStorageBuckets(unittest.TestCase):
    def setUp(self):
        self.cloud = GoogleCloudStorage()

        # Running into some issues creating and delete too many buckets, so
        # will check to see if it already exists
        if not self.cloud.bucket_exists(TEMP_BUCKET_NAME):
            self.cloud.create_bucket(TEMP_BUCKET_NAME)

            # Upload a file
            tmp_file_path = files.string_to_temp_file("A little string", suffix=".txt")
            self.cloud.put_blob(TEMP_BUCKET_NAME, TEMP_FILE_NAME, tmp_file_path)

    def test_list_buckets(self):
        # Assert that it finds the correct buckets
        bucket_list = self.cloud.list_buckets()

        # Make sure that my bucket is in the list
        self.assertIn(TEMP_BUCKET_NAME, bucket_list)

    def test_bucket_exists(self):
        # Assert finds a bucket that exists
        self.assertTrue(self.cloud.bucket_exists(TEMP_BUCKET_NAME))

        # Assert doesn't find a bucket that doesn't exist
        self.assertFalse(self.cloud.bucket_exists("NOT_A_REAL_BUCKET"))

    def test_get_bucket(self):
        # Assert that a bucket object is returned
        self.assertIsInstance(self.cloud.get_bucket(TEMP_BUCKET_NAME), storage.bucket.Bucket)

    def test_create_bucket(self):
        # Temporary bucket has already been created as part of set up, so just checking
        # that it really exists
        self.assertTrue(self.cloud.bucket_exists(TEMP_BUCKET_NAME))

    def test_delete_bucket(self):
        # Create another bucket, delete it and make sure it doesn't exist
        self.cloud.create_bucket(TEMP_BUCKET_NAME + "_2")
        self.cloud.delete_bucket(TEMP_BUCKET_NAME + "_2")
        self.assertFalse(self.cloud.bucket_exists(TEMP_BUCKET_NAME + "_2"))

    def test_list_blobs(self):
        blob_list = self.cloud.list_blobs(TEMP_BUCKET_NAME)

        # Make sure that my file is in the list
        self.assertIn(TEMP_FILE_NAME, blob_list)

        # Make sure that there is only one file in the bucket
        self.assertEqual(len(blob_list), 1)

    def test_blob_exists(self):
        # Assert that it thinks that the blob exists
        self.assertTrue(self.cloud.blob_exists(TEMP_BUCKET_NAME, TEMP_FILE_NAME))

        # Assert that it thinks that a non-existent blob doesn't exist
        self.assertFalse(self.cloud.blob_exists(TEMP_BUCKET_NAME, "FAKE_BLOB"))

    def test_put_blob(self):
        # Already being tested as part of setUp
        pass

    def test_get_blob(self):
        # Assert that a blob object is returned
        self.assertIsInstance(
            self.cloud.get_blob(TEMP_BUCKET_NAME, TEMP_FILE_NAME), storage.blob.Blob
        )

    def test_download_blob(self):
        # Download blob and ensure that it is the expected file
        path = self.cloud.download_blob(TEMP_BUCKET_NAME, TEMP_FILE_NAME)
        with open(path) as f:
            self.assertEqual(f.read(), "A little string")

    def test_delete_blob(self):
        file_name = "delete_me.txt"

        # Upload a file
        tmp_file_path = files.string_to_temp_file("A little string", suffix=".txt")
        self.cloud.put_blob(TEMP_BUCKET_NAME, file_name, tmp_file_path)

        # Check that it was deleted.
        self.cloud.delete_blob(TEMP_BUCKET_NAME, file_name)
        self.assertFalse(self.cloud.blob_exists(TEMP_BUCKET_NAME, file_name))

    def test_get_url(self):
        file_name = "delete_me.csv"
        input_tbl = Table([["a"], ["1"]])
        self.cloud.upload_table(input_tbl, TEMP_BUCKET_NAME, file_name)
        url = self.cloud.get_url(TEMP_BUCKET_NAME, file_name)
        download_tbl = Table.from_csv(url)
        assert_matching_tables(input_tbl, download_tbl)
