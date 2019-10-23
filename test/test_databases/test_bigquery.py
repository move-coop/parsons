import unittest
import unittest.mock as mock
from parsons.databases.bigquery import BigQuery


# Test class to fake the RowIterator interface for BigQuery job results
class FakeResults:
    def __init__(self, data):
        self.data = data
        self.total_rows = len(data)

    def __iter__(self):
        return iter(self.data)


class TestBigQuery(unittest.TestCase):
    def test_query(self):
        query_string = 'select * from table'
        client_class = self._build_mock_client_class([{'one': 1, 'two': 2}])

        # Pass the mock class into our BigQuery constructor
        bq = BigQuery(client_class=client_class)

        # Run a query against our parsons BigQuery class
        result = bq.query(query_string)

        # Check our return value
        self.assertEqual(result.num_rows, 1)
        self.assertEqual(result.columns, ['one', 'two'])
        self.assertEqual(result[0], {'one': 1, 'two': 2})

        # Make sure our client class constructor was called.
        self.assertEqual(client_class.call_count, 1)
        self.assertEqual(client_class.call_args[1]['project'], None)
        self.assertEqual(client_class.call_args[1]['credentials'], None)
        self.assertEqual(client_class.call_args[1]['location'], None)

    def test_query__no_results(self):
        query_string = 'select * from table'
        client_class = self._build_mock_client_class([])

        # Pass the mock class into our BigQuery constructor
        bq = BigQuery(client_class=client_class)

        # Run a query against our parsons BigQuery class
        result = bq.query(query_string)

        # Check our return value
        self.assertEqual(result, None)

    def test_query__custom_params(self):
        # For our purposes here, we don't care the value type.. just want to make sure things
        # are passed around as expected
        credentials = {'some': 'values'}
        location = 'US'
        project_id = 'project'

        client_class = self._build_mock_client_class([{'one': 1, 'two': 2}])

        # Pass the mock class into our BigQuery constructor
        bq = BigQuery(project=project_id, credentials=credentials, location=location,
                      client_class=client_class)

        # Run a query against our parsons BigQuery class
        _ = bq.query('select * from table')

        # Make sure our client class constructor was called with the values we passed to the
        # BigQuery class
        self.assertEqual(client_class.call_count, 1)
        self.assertEqual(client_class.call_args[1]['project'], project_id)
        self.assertEqual(client_class.call_args[1]['credentials'], credentials)
        self.assertEqual(client_class.call_args[1]['location'], location)

    def _build_mock_client_class(self, results):
        # Create a mock that will play the role of the query job
        query_job = mock.MagicMock()
        query_job.result.return_value = FakeResults(results)

        # Create a mock that will play the role of our BigQuery client
        client = mock.MagicMock()
        client.query.return_value = query_job

        # Create a mock that will serve as our BigQuery Client class __init__
        client_class = mock.MagicMock()
        client_class.return_value = client

        return client_class
