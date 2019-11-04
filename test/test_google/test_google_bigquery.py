import os
import unittest
import unittest.mock as mock
from parsons.google.google_bigquery import GoogleBigQuery


# Test class to fake the RowIterator interface for BigQuery job results
class FakeResults:
    def __init__(self, data):
        self.data = data
        self.total_rows = len(data)

    def __iter__(self):
        return iter(self.data)


class TestGoogleBigQuery(unittest.TestCase):
    def test_query(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'foo'

        query_string = 'select * from table'

        # Pass the mock class into our GoogleBigQuery constructor
        bq = GoogleBigQuery()
        bq._client = self._build_mock_client([{'one': 1, 'two': 2}])

        # Run a query against our parsons GoogleBigQuery class
        result = bq.query(query_string)

        # Check our return value
        self.assertEqual(result.num_rows, 1)
        self.assertEqual(result.columns, ['one', 'two'])
        self.assertEqual(result[0], {'one': 1, 'two': 2})

    def test_query__no_results(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'foo'

        query_string = 'select * from table'

        # Pass the mock class into our GoogleBigQuery constructor
        bq = GoogleBigQuery()
        bq._client = self._build_mock_client([])

        # Run a query against our parsons GoogleBigQuery class
        result = bq.query(query_string)

        # Check our return value
        self.assertEqual(result, None)

    def _build_mock_client(self, results):
        # Create a mock that will play the role of the query job
        query_job = mock.MagicMock()
        query_job.result.return_value = FakeResults(results)

        # Create a mock that will play the role of our GoogleBigQuery client
        client = mock.MagicMock()
        client.query.return_value = query_job

        return client
