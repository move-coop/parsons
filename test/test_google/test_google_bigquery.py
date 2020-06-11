import os
import unittest
import unittest.mock as mock
from google.cloud import bigquery
from google.cloud import exceptions
from parsons.google.google_bigquery import GoogleBigQuery
from parsons.etl import Table


class TestGoogleBigQuery(unittest.TestCase):
    def setUp(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'foo'
        self.tmp_gcs_bucket = 'tmp'

    def test_query(self):
        query_string = 'select * from table'

        # Pass the mock class into our GoogleBigQuery constructor
        bq = self._build_mock_client_for_querying([{'one': 1, 'two': 2}])

        # Run a query against our parsons GoogleBigQuery class
        result = bq.query(query_string)

        # Check our return value
        self.assertEqual(result.num_rows, 1)
        self.assertEqual(result.columns, ['one', 'two'])
        self.assertEqual(result[0], {'one': 1, 'two': 2})

    def test_query__no_results(self):
        query_string = 'select * from table'

        # Pass the mock class into our GoogleBigQuery constructor
        bq = self._build_mock_client_for_querying([])

        # Run a query against our parsons GoogleBigQuery class
        result = bq.query(query_string)

        # Check our return value
        self.assertEqual(result, None)

    def test_copy(self):
        # setup dependencies / inputs
        tmp_blob_uri = 'gs://tmp/file'

        # set up object under test
        gcs_client = self._build_mock_cloud_storage_client(tmp_blob_uri)
        tbl = self.default_table
        bq = self._build_mock_client_for_copying(table_exists=False)

        # call the method being tested
        bq.copy(tbl, 'dataset.table', tmp_gcs_bucket=self.tmp_gcs_bucket,
                gcs_client=gcs_client)

        # check that the method did the right things
        self.assertEqual(gcs_client.upload_table.call_count, 1)
        upload_call_args = gcs_client.upload_table.call_args
        self.assertEqual(upload_call_args[0][0], tbl)
        self.assertEqual(upload_call_args[0][1], self.tmp_gcs_bucket)
        tmp_blob_name = upload_call_args[0][2]

        self.assertEqual(bq.client.load_table_from_uri.call_count, 1)
        load_call_args = bq.client.load_table_from_uri.call_args
        self.assertEqual(load_call_args[0][0], tmp_blob_uri)

        job_config = load_call_args[1]['job_config']
        self.assertEqual(job_config.write_disposition,
                         bigquery.WriteDisposition.WRITE_EMPTY)

        # make sure we cleaned up the temp file
        self.assertEqual(gcs_client.delete_blob.call_count, 1)
        delete_call_args = gcs_client.delete_blob.call_args
        self.assertEqual(delete_call_args[0][0], self.tmp_gcs_bucket)
        self.assertEqual(delete_call_args[0][1], tmp_blob_name)

    def test_copy__if_exists_truncate(self):
        gcs_client = self._build_mock_cloud_storage_client()
        # set up object under test
        bq = self._build_mock_client_for_copying()

        # call the method being tested
        bq.copy(self.default_table, 'dataset.table', tmp_gcs_bucket=self.tmp_gcs_bucket,
                if_exists='truncate', gcs_client=gcs_client)

        # check that the method did the right things
        call_args = bq.client.load_table_from_uri.call_args
        job_config = call_args[1]['job_config']
        self.assertEqual(job_config.write_disposition,
                         bigquery.WriteDisposition.WRITE_TRUNCATE)

        # make sure we cleaned up the temp file
        self.assertEqual(gcs_client.delete_blob.call_count, 1)

    def test_copy__if_exists_append(self):
        gcs_client = self._build_mock_cloud_storage_client()
        # set up object under test
        bq = self._build_mock_client_for_copying()

        # call the method being tested
        bq.copy(self.default_table, 'dataset.table', tmp_gcs_bucket=self.tmp_gcs_bucket,
                if_exists='append', gcs_client=gcs_client)

        # check that the method did the right things
        call_args = bq.client.load_table_from_uri.call_args
        job_config = call_args[1]['job_config']
        self.assertEqual(job_config.write_disposition,
                         bigquery.WriteDisposition.WRITE_APPEND)

        # make sure we cleaned up the temp file
        self.assertEqual(gcs_client.delete_blob.call_count, 1)

    def test_copy__if_exists_fail(self):
        # set up object under test
        bq = self._build_mock_client_for_copying()

        # call the method being tested
        with self.assertRaises(Exception):
            bq.copy(self.default_table, 'dataset.table', tmp_gcs_bucket=self.tmp_gcs_bucket,
                    gcs_client=self._build_mock_cloud_storage_client())

    def test_copy__if_exists_drop(self):
        gcs_client = self._build_mock_cloud_storage_client()
        # set up object under test
        bq = self._build_mock_client_for_copying()

        # call the method being tested
        bq.copy(self.default_table, 'dataset.table', tmp_gcs_bucket=self.tmp_gcs_bucket,
                if_exists='drop', gcs_client=gcs_client)

        # check that we tried to delete the table
        self.assertEqual(bq.client.delete_table.call_count, 1)

        # make sure we cleaned up the temp file
        self.assertEqual(gcs_client.delete_blob.call_count, 1)

    def test_copy__bad_if_exists(self):
        gcs_client = self._build_mock_cloud_storage_client()

        # set up object under test
        bq = self._build_mock_client_for_copying()

        # call the method being tested
        with self.assertRaises(ValueError):
            bq.copy(self.default_table, 'dataset.table', tmp_gcs_bucket=self.tmp_gcs_bucket,
                    if_exists='foo', gcs_client=gcs_client)

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

        bq = GoogleBigQuery()
        bq._client = client
        bq._dbapi = dbapi
        return bq

    def _build_mock_client_for_copying(self, table_exists=True):
        bq_client = mock.MagicMock()
        if not table_exists:
            bq_client.get_table.side_effect = exceptions.NotFound('not found')
        bq = GoogleBigQuery()
        bq._client = bq_client
        return bq

    def _build_mock_cloud_storage_client(self, tmp_blob_uri=''):
        gcs_client = mock.MagicMock()
        gcs_client.upload_table.return_value = tmp_blob_uri
        return gcs_client

    @property
    def default_table(self):
        return Table([
            {'num': 1, 'ltr': 'a'},
            {'num': 2, 'ltr': 'b'},
        ])
