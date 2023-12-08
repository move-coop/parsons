import json
import os
import unittest.mock as mock

from google.cloud import bigquery
from google.cloud import exceptions

from parsons import GoogleBigQuery as BigQuery, Table
from parsons.google.google_cloud_storage import GoogleCloudStorage
from test.test_google.test_utilities import FakeCredentialTest


class FakeClient:
    """A Fake Storage Client used for monkey-patching."""

    def __init__(self, project=None):
        self.project = project


class FakeGoogleCloudStorage(GoogleCloudStorage):
    """A Fake GoogleCloudStorage object used to test setting up credentials."""

    @mock.patch("google.cloud.storage.Client", FakeClient)
    def __init__(self):
        super().__init__(None, None)

    def upload_table(
        self, table, bucket_name, blob_name, data_type="csv", default_acl=None
    ):
        pass

    def delete_blob(self, bucket_name, blob_name):
        pass


class TestGoogleBigQuery(FakeCredentialTest):
    def setUp(self):
        super().setUp()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.cred_path
        self.tmp_gcs_bucket = "tmp"

    def tearDown(self) -> None:
        super().tearDown()
        del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

    def test_query(self):
        query_string = "select * from table"

        # Pass the mock class into our GoogleBigQuery constructor
        bq = self._build_mock_client_for_querying([{"one": 1, "two": 2}])

        # Run a query against our parsons GoogleBigQuery class
        result = bq.query(query_string)

        # Check our return value
        self.assertEqual(result.num_rows, 1)
        self.assertEqual(result.columns, ["one", "two"])
        self.assertEqual(result[0], {"one": 1, "two": 2})

    def test_query__no_results(self):
        query_string = "select * from table"

        # Pass the mock class into our GoogleBigQuery constructor
        bq = self._build_mock_client_for_querying([])

        # Run a query against our parsons GoogleBigQuery class
        result = bq.query(query_string)

        # Check our return value
        self.assertEqual(result, None)

    @mock.patch("parsons.utilities.files.create_temp_file")
    def test_query__no_return(self, create_temp_file_mock):
        query_string = "select * from table"

        # Pass the mock class into our GoogleBigQuery constructor
        bq = self._build_mock_client_for_querying([{"one": 1, "two": 2}])
        bq._fetch_query_results = mock.MagicMock()

        # Run a query against our parsons GoogleBigQuery class
        result = bq.query(query_string, return_values=False)

        # Check our return value
        self.assertEqual(result, None)

        # Check that query results were not fetched
        bq._fetch_query_results.assert_not_called()

    @mock.patch("parsons.utilities.files.create_temp_file")
    def test_query_with_transaction(self, create_temp_file_mock):
        queries = ["select * from table", "select foo from bar"]
        parameters = ["baz"]

        # Pass the mock class into our GoogleBigQuery constructor
        bq = self._build_mock_client_for_querying([{"one": 1, "two": 2}])
        bq.query = mock.MagicMock()

        # Run a query against our parsons GoogleBigQuery class
        result = bq.query_with_transaction(queries=queries, parameters=parameters)
        keyword_args = bq.query.call_args[1]

        # Check our return value
        self.assertEqual(result, None)

        # Check that queries and transaction keywords are included in sql
        self.assertTrue(
            all(
                [
                    text in keyword_args["sql"]
                    for text in queries + ["BEGIN TRANSACTION", "COMMIT"]
                ]
            )
        )
        self.assertEqual(keyword_args["parameters"], parameters)
        self.assertFalse(keyword_args["return_values"])

    def test_copy_gcs(self):
        # setup dependencies / inputs
        tmp_blob_uri = "gs://tmp/file"

        # set up object under test
        bq = self._build_mock_client_for_copying(table_exists=False)

        # call the method being tested
        bq.copy_from_gcs(
            gcs_blob_uri=tmp_blob_uri,
            table_name="dataset.table",
        )

        # check that the method did the right things
        self.assertEqual(bq.client.load_table_from_uri.call_count, 1)
        load_call_args = bq.client.load_table_from_uri.call_args
        self.assertEqual(load_call_args[1]["source_uris"], tmp_blob_uri)

        job_config = load_call_args[1]["job_config"]
        self.assertEqual(
            job_config.write_disposition, bigquery.WriteDisposition.WRITE_EMPTY
        )

    def test_copy_gcs__if_exists_truncate(self):
        # setup dependencies / inputs
        tmp_blob_uri = "gs://tmp/file"

        # set up object under test
        bq = self._build_mock_client_for_copying(table_exists=False)

        # call the method being tested
        bq.copy_from_gcs(
            gcs_blob_uri=tmp_blob_uri,
            table_name="dataset.table",
            if_exists="truncate",
        )

        # check that the method did the right things
        self.assertEqual(bq.client.load_table_from_uri.call_count, 1)
        load_call_args = bq.client.load_table_from_uri.call_args
        self.assertEqual(load_call_args[1]["source_uris"], tmp_blob_uri)

        job_config = load_call_args[1]["job_config"]
        self.assertEqual(
            job_config.write_disposition, bigquery.WriteDisposition.WRITE_TRUNCATE
        )

    def test_copy_gcs__if_exists_append(self):
        # setup dependencies / inputs
        tmp_blob_uri = "gs://tmp/file"

        # set up object under test
        bq = self._build_mock_client_for_copying(table_exists=False)

        # call the method being tested
        bq.copy_from_gcs(
            gcs_blob_uri=tmp_blob_uri,
            table_name="dataset.table",
            if_exists="append",
        )

        # check that the method did the right things
        self.assertEqual(bq.client.load_table_from_uri.call_count, 1)
        load_call_args = bq.client.load_table_from_uri.call_args
        self.assertEqual(load_call_args[1]["source_uris"], tmp_blob_uri)

        job_config = load_call_args[1]["job_config"]
        self.assertEqual(
            job_config.write_disposition, bigquery.WriteDisposition.WRITE_APPEND
        )

    def test_copy_gcs__if_exists_fail(self):
        # setup dependencies / inputs
        tmp_blob_uri = "gs://tmp/file"

        # set up object under test
        bq = self._build_mock_client_for_copying(table_exists=False)

        # call the method being tested
        bq.copy_from_gcs(
            gcs_blob_uri=tmp_blob_uri,
            table_name="dataset.table",
            if_exists="truncate",
        )
        bq.table_exists = mock.MagicMock()
        bq.table_exists.return_value = True

        # call the method being tested
        with self.assertRaises(Exception):
            bq.copy_from_gcs(
                self.default_table,
                "dataset.table",
                tmp_gcs_bucket=self.tmp_gcs_bucket,
                gcs_client=self._build_mock_cloud_storage_client(),
            )

    def test_copy_gcs__if_exists_drop(self):
        # setup dependencies / inputs
        tmp_blob_uri = "gs://tmp/file"

        # set up object under test
        bq = self._build_mock_client_for_copying(table_exists=False)
        bq.table_exists = mock.MagicMock()
        bq.table_exists.return_value = True

        # call the method being tested
        bq.copy_from_gcs(
            gcs_blob_uri=tmp_blob_uri,
            table_name="dataset.table",
            if_exists="drop",
        )

        # check that we tried to delete the table
        self.assertEqual(bq.client.delete_table.call_count, 1)

    def test_copy_gcs__bad_if_exists(self):
        # setup dependencies / inputs
        tmp_blob_uri = "gs://tmp/file"

        # set up object under test
        bq = self._build_mock_client_for_copying(table_exists=False)
        bq.table_exists = mock.MagicMock()
        bq.table_exists.return_value = True

        # call the method being tested
        with self.assertRaises(ValueError):
            bq.copy_from_gcs(
                gcs_blob_uri=tmp_blob_uri,
                table_name="dataset.table",
                if_exists="foobar",
            )

    @mock.patch("google.cloud.storage.Client")
    @mock.patch.object(
        GoogleCloudStorage, "split_uri", return_value=("tmp", "file.gzip")
    )
    @mock.patch.object(
        GoogleCloudStorage, "unzip_blob", return_value="gs://tmp/file.csv"
    )
    def test_copy_large_compressed_file_from_gcs(
        self, unzip_mock: mock.MagicMock, split_mock: mock.MagicMock, *_
    ):
        # setup dependencies / inputs
        tmp_blob_uri = "gs://tmp/file.gzip"

        # set up object under test
        bq = self._build_mock_client_for_copying(table_exists=False)

        # call the method being tested
        bq.copy_large_compressed_file_from_gcs(
            gcs_blob_uri=tmp_blob_uri,
            table_name="dataset.table",
        )

        # check that the method did the right things
        split_mock.assert_has_calls(
            [
                mock.call(gcs_uri="gs://tmp/file.gzip"),
                mock.call(gcs_uri="gs://tmp/file.csv"),
            ]
        )
        unzip_mock.assert_called_once_with(
            bucket_name="tmp",
            blob_name="file.gzip",
            new_file_extension="csv",
            compression_type="gzip",
        )
        self.assertEqual(bq.client.load_table_from_uri.call_count, 1)
        load_call_args = bq.client.load_table_from_uri.call_args
        self.assertEqual(load_call_args[1]["source_uris"], "gs://tmp/file.csv")

        job_config = load_call_args[1]["job_config"]
        self.assertEqual(
            job_config.write_disposition, bigquery.WriteDisposition.WRITE_EMPTY
        )

    def test_copy_s3(self):
        # setup dependencies / inputs
        table_name = "table_name"
        bucket = "aws_bucket"
        key = "file.gzip"
        aws_access_key_id = "AAAAAA"
        aws_secret_access_key = "BBBBB"
        tmp_gcs_bucket = "tmp"

        # set up object under test
        bq = self._build_mock_client_for_copying(table_exists=False)
        gcs_client = self._build_mock_cloud_storage_client()
        bq.copy_from_gcs = mock.MagicMock()

        # call the method being tested
        bq.copy_s3(
            table_name=table_name,
            bucket=bucket,
            key=key,
            gcs_client=gcs_client,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            tmp_gcs_bucket=tmp_gcs_bucket,
        )

        # check that the method did the right things
        gcs_client.copy_s3_to_gcs.assert_called_once_with(
            aws_source_bucket=bucket,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            gcs_sink_bucket=tmp_gcs_bucket,
            aws_s3_key=key,
        )
        bq.copy_from_gcs.assert_called_once()
        gcs_client.delete_blob.assert_called_once()

    def test_copy(self):
        # setup dependencies / inputs
        tmp_blob_uri = "gs://tmp/file"

        # set up object under test
        gcs_client = self._build_mock_cloud_storage_client(tmp_blob_uri)
        tbl = self.default_table
        bq = self._build_mock_client_for_copying(table_exists=False)
        bq.copy_from_gcs = mock.MagicMock()
        table_name = ("dataset.table",)

        # call the method being tested
        bq.copy(
            tbl,
            table_name,
            tmp_gcs_bucket=self.tmp_gcs_bucket,
            gcs_client=gcs_client,
        )

        # check that the method did the right things
        self.assertEqual(gcs_client.upload_table.call_count, 1)
        upload_call_args = gcs_client.upload_table.call_args
        self.assertEqual(upload_call_args[0][0], tbl)
        self.assertEqual(upload_call_args[0][1], self.tmp_gcs_bucket)
        tmp_blob_name = upload_call_args[0][2]

        self.assertEqual(bq.copy_from_gcs.call_count, 1)
        load_call_args = bq.copy_from_gcs.call_args
        self.assertEqual(load_call_args[1]["gcs_blob_uri"], tmp_blob_uri)
        self.assertEqual(load_call_args[1]["table_name"], table_name)

        # make sure we cleaned up the temp file
        self.assertEqual(gcs_client.delete_blob.call_count, 1)
        delete_call_args = gcs_client.delete_blob.call_args
        self.assertEqual(delete_call_args[0][0], self.tmp_gcs_bucket)
        self.assertEqual(delete_call_args[0][1], tmp_blob_name)

    def test_copy__credentials_are_correctly_set(self):
        tbl = self.default_table
        bq = self._build_mock_client_for_copying(table_exists=False)

        # Pass in our fake GCS Client.
        bq.copy(
            tbl,
            "dataset.table",
            tmp_gcs_bucket=self.tmp_gcs_bucket,
            gcs_client=FakeGoogleCloudStorage(),
        )

        actual = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

        with open(actual, "r") as factual:
            with open(self.cred_path, "r") as fexpected:
                actual_str = factual.read()
                self.assertEqual(actual_str, fexpected.read())
                self.assertEqual(self.cred_contents, json.loads(actual_str))

    def test_copy__if_exists_passed_through(self):
        # setup dependencies / inputs
        tmp_blob_uri = "gs://tmp/file"

        # set up object under test
        gcs_client = self._build_mock_cloud_storage_client(tmp_blob_uri)
        tbl = self.default_table
        bq = self._build_mock_client_for_copying(table_exists=False)
        bq.copy_from_gcs = mock.MagicMock()
        table_name = "dataset.table"
        if_exists = "append"

        # call the method being tested
        bq.copy(
            tbl,
            table_name,
            tmp_gcs_bucket=self.tmp_gcs_bucket,
            gcs_client=gcs_client,
            if_exists=if_exists,
        )

        self.assertEqual(bq.copy_from_gcs.call_count, 1)
        load_call_args = bq.copy_from_gcs.call_args
        self.assertEqual(load_call_args[1]["if_exists"], if_exists)

    @mock.patch.object(BigQuery, "table_exists", return_value=False)
    @mock.patch.object(BigQuery, "query", return_value=None)
    def test_duplicate_table(self, query_mock, table_exists_mock):
        source_table = "vendor_table"
        destination_table = "raw_table"
        expected_query = f"""
            CREATE TABLE
            {destination_table}
            CLONE {source_table}
        """
        bq = self._build_mock_client_for_querying(results=None)

        bq.duplicate_table(
            source_table=source_table,
            destination_table=destination_table,
        )

        query_mock.assert_called_once()
        actual_query = query_mock.call_args[1]["sql"]
        self.assertEqual(actual_query, expected_query)

    @mock.patch.object(BigQuery, "table_exists", return_value=False)
    @mock.patch.object(BigQuery, "delete_table", return_value=None)
    @mock.patch.object(BigQuery, "query", return_value=None)
    def test_duplicate_table_with_drop(
        self, query_mock: mock.MagicMock, delete_mock: mock.MagicMock, table_exists_mock
    ):
        source_table = "vendor_table"
        destination_table = "raw_table"
        bq = self._build_mock_client_for_querying(results=None)

        bq.duplicate_table(
            source_table=source_table,
            destination_table=destination_table,
            drop_source_table=True,
        )

        delete_mock.assert_called_once_with(table_name=source_table)

    @mock.patch.object(BigQuery, "table_exists", return_value=True)
    @mock.patch.object(BigQuery, "query_with_transaction", return_value=None)
    @mock.patch.object(BigQuery, "copy", return_value=None)
    def test_upsert(self, copy_mock, query_mock, *_):
        upsert_tbl = Table([["id", "name"], [1, "Jane"]])
        target_table = "my_dataset.my_target_table"
        primary_key = "id"
        bq = self._build_mock_client_for_querying(results=[])

        bq.upsert(
            table_obj=upsert_tbl,
            target_table=target_table,
            primary_key=primary_key,
            distinct_check=False,
        )

        # stages the table -> calls copy
        copy_mock.assert_called_once()
        self.assertEqual(copy_mock.call_args[1]["tbl"], upsert_tbl)
        self.assertEqual(copy_mock.call_args[1]["template_table"], target_table)

        # runs a delete insert within a transaction
        query_mock.assert_called_once()
        actual_queries = query_mock.call_args[1]["queries"]
        self.assertIn("DELETE", actual_queries[0])
        self.assertIn("INSERT", actual_queries[1])

    @mock.patch.object(BigQuery, "query")
    def test_get_row_count(self, query_mock):
        # Arrange
        schema = "foo"
        table_name = "bar"
        expected_num_rows = 2

        query_mock.return_value = Table([{"row_count": expected_num_rows}])
        expected_query = f"SELECT COUNT(*) AS row_count FROM `{schema}.{table_name}`"
        bq = self._build_mock_client_for_querying(results=Table([{"row_count": 2}]))

        # Act
        row_count = bq.get_row_count(schema=schema, table_name=table_name)

        # Assert
        query_mock.assert_called_once()
        actual_query = query_mock.call_args[1]["sql"]
        self.assertEqual(row_count, expected_num_rows)
        self.assertEqual(actual_query, expected_query)

    def _build_mock_client_for_querying(self, results):
        # Create a mock that will play the role of the cursor
        cursor = mock.MagicMock()
        cursor.execute.return_value = None
        cursor.fetchmany.side_effect = [results, []]

        # Create a mock that will play the role of the connection
        connection = mock.MagicMock()
        connection.cursor.return_value = cursor

        # Create a mock that will play the role of the Google BigQuery dbapi module
        dbapi = mock.MagicMock()
        dbapi.connect.return_value = connection

        # Create a mock that will play the role of our GoogleBigQuery client
        client = mock.MagicMock()

        bq = BigQuery()
        bq._client = client
        bq._dbapi = dbapi
        return bq

    def _build_mock_client_for_copying(self, table_exists=True):
        bq_client = mock.MagicMock()
        if not table_exists:
            bq_client.get_table.side_effect = exceptions.NotFound("not found")
        bq = BigQuery()
        bq._client = bq_client
        return bq

    def _build_mock_cloud_storage_client(self, tmp_blob_uri=""):
        gcs_client = mock.MagicMock()
        gcs_client.upload_table.return_value = tmp_blob_uri
        return gcs_client

    @property
    def default_table(self):
        return Table(
            [
                {"num": 1, "ltr": "a"},
                {"num": 2, "ltr": "b"},
            ]
        )
