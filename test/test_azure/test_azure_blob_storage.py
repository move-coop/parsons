import os
import unittest
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from azure.storage.blob import BlobClient, ContainerClient

from parsons import AzureBlobStorage, Table
from parsons.utilities import files

TEST_ACCOUNT_NAME = os.getenv("PARSONS_AZURE_ACCOUNT_NAME")
TEST_CREDENTIAL = os.getenv("PARSONS_AZURE_CREDENTIAL")
TEST_CONTAINER_NAME = os.getenv("PARSONS_AZURE_CONTAINER_NAME")
TEST_FILE_NAME = "tmp_file_01.txt"
TEST_FILE_CONTENTS = "Test"


@unittest.skipIf(not os.getenv("LIVE_TEST"), "Skipping because not running live test")
class TestAzureBlobStorage(unittest.TestCase):
    def setUp(self):
        self.azure_blob = AzureBlobStorage(
            account_name=TEST_ACCOUNT_NAME, credential=TEST_CREDENTIAL
        )

        # Create the container if it does not exist already
        if not self.azure_blob.container_exists(TEST_CONTAINER_NAME):
            self.azure_blob.create_container(TEST_CONTAINER_NAME)

        # Create blob if it doesn't exist already
        if not self.azure_blob.blob_exists(TEST_CONTAINER_NAME, TEST_FILE_NAME):
            tmp_file_path = files.string_to_temp_file(TEST_FILE_CONTENTS, suffix=".txt")
            self.azure_blob.put_blob(TEST_CONTAINER_NAME, TEST_FILE_NAME, tmp_file_path)

    def test_list_containers(self):
        # Make sure container created in setup is in the list
        container_list = self.azure_blob.list_containers()
        self.assertIn(TEST_CONTAINER_NAME, container_list)

    def test_container_exists(self):
        # Assert that setup container exists
        self.assertTrue(self.azure_blob.container_exists(TEST_CONTAINER_NAME))

        # Assert that invalid bucket does not exists
        self.assertFalse(self.azure_blob.container_exists("fakecontainer"))

    def test_get_container(self):
        # Assert that a ContainerClient object is returned
        self.assertIsInstance(self.azure_blob.get_container(TEST_CONTAINER_NAME), ContainerClient)

    def test_create_container(self):
        # Assert that container created in setup exists
        self.assertTrue(self.azure_blob.container_exists(TEST_CONTAINER_NAME))

        # Add current datetime microseconds for randomness to avoid intermittent failures
        dt_microseconds = datetime.now().isoformat()[-6:]
        create_container_name = f"{TEST_CONTAINER_NAME}create{dt_microseconds}"

        # Create a new container with metadata, assert that it is included
        create_container = self.azure_blob.create_container(
            create_container_name, metadata={"testing": "parsons"}
        )
        create_container_properties = create_container.get_container_properties()
        self.assertIn("testing", create_container_properties.metadata)

        # Delete the container after the assertion
        self.azure_blob.delete_container(create_container_name)

    def test_delete_container(self):
        # Add current datetime microseconds for randomness to avoid intermittent failures
        dt_microseconds = datetime.now().isoformat()[-6:]
        delete_container_name = f"{TEST_CONTAINER_NAME}delete{dt_microseconds}"

        # Create an additional container, assert that it exists
        self.azure_blob.create_container(delete_container_name)
        self.assertTrue(self.azure_blob.container_exists(delete_container_name))

        # Then delete the container and assert it does not exist
        self.azure_blob.delete_container(delete_container_name)
        self.assertFalse(self.azure_blob.container_exists(delete_container_name))

    def test_list_blobs(self):
        blob_name_list = self.azure_blob.list_blobs(TEST_CONTAINER_NAME)

        # Assert that file created in setup is in the list
        self.assertIn(TEST_FILE_NAME, blob_name_list)

    def test_blob_exists(self):
        # Assert that blob created in setup exists
        self.assertTrue(self.azure_blob.blob_exists(TEST_CONTAINER_NAME, TEST_FILE_NAME))

        # Assert that invalid blob does not exist
        self.assertFalse(self.azure_blob.blob_exists(TEST_CONTAINER_NAME, "FAKE_BLOB"))

    def test_get_blob(self):
        # Assert that get_blob returns a BlobClient object for blob created in setup
        self.assertIsInstance(
            self.azure_blob.get_blob(TEST_CONTAINER_NAME, TEST_FILE_NAME), BlobClient
        )

    def test_get_blob_url(self):
        # Assert that get_blob_url returns a URL with a shared access signature
        blob_url = self.azure_blob.get_blob_url(TEST_CONTAINER_NAME, TEST_FILE_NAME, permission="r")
        parsed_blob_url = urlparse(blob_url)
        parsed_blob_query = parse_qs(parsed_blob_url.query)
        self.assertIn("sas", parsed_blob_query)

    def test_put_blob(self):
        # Assert that put_blob returns a BlobClient object
        put_blob_name = "tmp_file_put.txt"
        tmp_file_path = files.string_to_temp_file("Test", suffix=".txt")

        put_blob_client = self.azure_blob.put_blob(
            TEST_CONTAINER_NAME, put_blob_name, tmp_file_path
        )
        self.assertIsInstance(put_blob_client, BlobClient)

        self.azure_blob.delete_blob(TEST_CONTAINER_NAME, put_blob_name)

    def test_download_blob(self):
        # Download blob and ensure that it has the expected file contents
        download_blob_path = self.azure_blob.download_blob(TEST_CONTAINER_NAME, TEST_FILE_NAME)
        with open(download_blob_path) as f:
            self.assertEqual(f.read(), TEST_FILE_CONTENTS)

    def test_delete_blob(self):
        delete_blob_name = "delete_blob.txt"

        # Upload a blob, assert that it exists
        tmp_file_path = files.string_to_temp_file(TEST_FILE_CONTENTS, suffix=".txt")
        self.azure_blob.put_blob(TEST_CONTAINER_NAME, delete_blob_name, tmp_file_path)
        self.assertTrue(self.azure_blob.blob_exists(TEST_CONTAINER_NAME, delete_blob_name))

        # Delete the blob, assert that it no longer exists
        self.azure_blob.delete_blob(TEST_CONTAINER_NAME, delete_blob_name)
        self.assertFalse(self.azure_blob.blob_exists(TEST_CONTAINER_NAME, delete_blob_name))

    def test_upload_table(self):
        test_table = Table([{"first": "Test", "last": "Person"}])
        test_table_blob_name = "table.csv"

        # Upload a test table as CSV, assert that blob is a CSV
        table_blob_client = self.azure_blob.upload_table(
            test_table, TEST_CONTAINER_NAME, test_table_blob_name, data_type="csv"
        )
        table_blob_client_properties = table_blob_client.get_blob_properties()
        self.assertEqual(table_blob_client_properties.content_settings.content_type, "text/csv")

        # Remove blob after assertion
        self.azure_blob.delete_blob(TEST_CONTAINER_NAME, test_table_blob_name)
