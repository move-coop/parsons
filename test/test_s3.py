import unittest
import os
from datetime import datetime
import pytz
from parsons import S3, Table
import urllib
import time
from test.utils import assert_matching_tables

# Requires a s3 credentials stored in aws config or env variable
# to run properly.


@unittest.skipIf(not os.environ.get("LIVE_TEST"), "Skipping because not running live test")
class TestS3(unittest.TestCase):
    def setUp(self):

        self.s3 = S3()

        self.s3.aws.session.get_credentials()

        # Create a new bucket
        self.test_bucket = os.environ["S3_TEMP_BUCKET"]
        # Trying miss random errors on not finding buckets
        self.s3.create_bucket(self.test_bucket)

        self.test_key = "test.csv"
        self.tbl = Table([{"first": "Bob", "last": "Smith"}])
        csv_path = self.tbl.to_csv()

        self.test_incoming_prefix = "incoming"
        self.test_processing_prefix = "processing"
        self.test_dest_prefix = "archive"

        self.test_key_2 = "test2.csv"
        self.tbl_2 = Table([{"first": "Jack", "last": "Smith"}])
        csv_path_2 = self.tbl_2.to_csv()

        self.test_bucket_subname = self.test_bucket.split("-")[0]

        # Sometimes it runs into issues putting the file
        retry = 1

        while retry <= 5:
            try:
                # Put a test file in the bucket
                self.s3.put_file(self.test_bucket, self.test_key, csv_path)
                self.s3.put_file(self.test_bucket, self.test_key_2, csv_path_2)
                break
            except Exception:
                print("Retrying putting file in bucket...")
                retry += 1

    def tearDown(self):
        for k in self.s3.list_keys(self.test_bucket):
            self.s3.remove_file(self.test_bucket, k)

    def test_list_buckets(self):

        # Also tests that create_bucket works (part of setup)

        buckets = self.s3.list_buckets()
        self.assertTrue(self.test_bucket in buckets)

    def test_bucket_exists(self):

        # Test that a bucket that exists returns True
        self.assertTrue(self.s3.bucket_exists(self.test_bucket))

        # Test that a bucket that doesn't exist returns False
        self.assertFalse(self.s3.bucket_exists("idontexist_bucket"))

    def test_list_keys(self):

        # Put a file in the bucket
        csv_path = self.tbl.to_csv()
        key = "test/test.csv"
        self.s3.put_file(self.test_bucket, key, csv_path)

        # Test that basic bucket list works
        keys = self.s3.list_keys(self.test_bucket, prefix="test/test")
        self.assertTrue(key in keys)

        # Test that prefix filter works -- when there
        keys = self.s3.list_keys(self.test_bucket, prefix="test")
        self.assertTrue(key in keys)

        # Test that prefix filter works -- when not there
        keys = self.s3.list_keys(self.test_bucket, prefix="nope")
        self.assertFalse(key in keys)

    def test_key_exists(self):

        csv_path = self.tbl.to_csv()
        key = "test/test.csv"
        self.s3.put_file(self.test_bucket, key, csv_path)

        # Test that returns True if key exists
        self.assertTrue(self.s3.key_exists(self.test_bucket, key))

        # Test that returns True if key does not exist
        self.assertFalse(self.s3.key_exists(self.test_bucket, "akey"))

    def test_list_keys_suffix(self):

        # Put a file in the bucket
        csv_path = self.tbl.to_csv()
        key_1 = "test/test.csv"
        key_2 = "test/test.gz"
        self.s3.put_file(self.test_bucket, key_1, csv_path)
        self.s3.put_file(self.test_bucket, key_2, csv_path)

        keys = self.s3.list_keys(self.test_bucket, suffix="csv")
        self.assertTrue(key_1 in keys)
        self.assertFalse(key_2 in keys)

        keys = self.s3.list_keys(self.test_bucket, suffix="gz")
        self.assertFalse(key_1 in keys)
        self.assertTrue(key_2 in keys)

    def test_list_keys_date_modified(self):

        # Set current utc timestamp with timezone
        current_utc = datetime.utcnow().astimezone(pytz.utc)

        # Ensure the files created before now are included
        keys = self.s3.list_keys(self.test_bucket, date_modified_before=current_utc)
        self.assertEqual(len(keys), 2)

        # Ensure the files created after now are not included
        keys = self.s3.list_keys(self.test_bucket, date_modified_after=current_utc)
        self.assertEqual(len(keys), 0)

    def test_put_and_get_file(self):

        # put_file is part of setup, so just testing getting it here

        path = self.s3.get_file(self.test_bucket, self.test_key)
        result_tbl = Table.from_csv(path)
        assert_matching_tables(self.tbl, result_tbl)

    def test_get_url(self):

        # Test that you can download from URL
        url = self.s3.get_url(self.test_bucket, self.test_key)
        csv_table = Table.from_csv(url)
        assert_matching_tables(self.tbl, csv_table)

        # Test that the url expires
        url_short = self.s3.get_url(self.test_bucket, self.test_key, expires_in=1)
        time.sleep(2)
        with self.assertRaises(urllib.error.HTTPError) as cm:
            Table.from_csv(url_short)
        self.assertEqual(cm.exception.code, 403)

    def test_transfer_bucket(self):

        # Create a destination bucket
        # TODO maybe pull this from an env var as well
        destination_bucket = f"{self.test_bucket}-test"
        self.s3.create_bucket(destination_bucket)

        # Copy
        self.s3.transfer_bucket(self.test_bucket, self.test_key, destination_bucket)

        # Test that object made it
        path = self.s3.get_file(destination_bucket, self.test_key)
        result_tbl = Table.from_csv(path)
        assert_matching_tables(self.tbl, result_tbl)
        # Test that original still exists in original bucket
        self.assertTrue(self.s3.key_exists(self.test_bucket, self.test_key))

        # Transfer and delete original
        self.s3.transfer_bucket(
            self.test_bucket,
            self.test_key_2,
            destination_bucket,
            None,
            None,
            None,
            None,
            None,
            False,
            True,
        )
        path_2 = self.s3.get_file(destination_bucket, self.test_key_2)
        result_tbl_2 = Table.from_csv(path_2)
        assert_matching_tables(self.tbl_2, result_tbl_2)
        self.assertFalse(self.s3.key_exists(self.test_bucket, self.test_key_2))

    def test_get_buckets_with_subname(self):

        buckets_with_subname_true = self.s3.get_buckets_type(self.test_bucket_subname)
        self.assertTrue(self.test_bucket in buckets_with_subname_true)

        buckets_with_subname_false = self.s3.get_buckets_type("bucketsubnamedoesnotexist")
        self.assertFalse(self.test_bucket in buckets_with_subname_false)
