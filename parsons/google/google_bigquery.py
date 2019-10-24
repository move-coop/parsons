from google.cloud.bigquery import Client
from parsons import Table
from parsons.google.utitities import setup_google_application_credentials
from parsons.utilities.files import create_temp_file
import petl
import pickle


class BigQuery:
    """
    Class for querying BigQuery table and returning the data as Parsons tables.

    This class requires application credentials in the form of a json. It can be passed
    in the following ways:

    * Set an environmental variable named ``GOOGLE_APPLICATION_CREDENTIALS`` with the
      local path to the credentials json.

      Example: ``GOOGLE_APPLICATION_CREDENTALS='path/to/creds.json'``

    * Pass in the path to the credentials using the ``app_creds`` argument.

    * Pass in a json string using the ``app_creds`` argument.

    Args:
        project_id: str
            The project which the client is acting on behalf of. If not passed
            then will use the default inferred environment.
        app_creds: str
            A credentials json string or a path to a json file. Not required
            if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable set.
        location: str
            (optional) Default geographic location for tables
        client_class: obj
            (optional) Class to use use the BigQuery client
    """

    def __init__(self, app_creds=None, project=None, location=None, client_class=Client):
        setup_google_application_credentials(app_creds)

        self.project = project
        self.location = location
        self.client_class = client_class

    def query(self, query):
        """Run a BigQuery query and return the results as a Parsons table.

        `Args:`
            query: str
                A valid BigTable statement

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        # Create a BigQuery client to use to make the query
        client = self.client_class(project=self.project,
                                   location=self.location)

        # Run the query
        query_job = client.query(query)

        # We will use a temp file to cache the results so that they are not all living
        # in memory. We'll use pickle to serialize the results to file in order to maintain
        # the proper data types (e.g. integer).
        temp_filename = create_temp_file()

        wrote_header = False
        with open(temp_filename, 'wb') as temp_file:
            results = query_job.result()

            # If there are no results, just return None
            if results.total_rows == 0:
                return None

            for row in results:
                # Make sure we write out the header once and only once
                if not wrote_header:
                    wrote_header = True
                    header = list(row.keys())
                    pickle.dump(header, temp_file)

                row_data = list(row.values())
                pickle.dump(row_data, temp_file)

        ptable = petl.frompickle(temp_filename)
        final_table = Table(ptable)

        return final_table
