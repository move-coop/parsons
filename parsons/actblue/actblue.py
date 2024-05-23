import logging
import time
from parsons.utilities.api_connector import APIConnector
from parsons.utilities import check_env
from parsons.etl import Table

logger = logging.getLogger(__name__)

POLLING_DELAY = 1
ACTBLUE_API_ENDPOINT = "https://secure.actblue.com/api/v1"


class ActBlue(object):
    """
    Instantiate class.

       `Args:`
            actblue_client_uuid: str
                The ActBlue provided Client UUID. Not required if ``ACTBLUE_CLIENT_UUID`` env
                variable set.
            actblue_client_secret: str
                The ActBlue provided Client Secret. Not required if ``ACTBLUE_CLIENT_SECRET`` env
                variable set.
            actblue_uri: str
                The URI to access the CSV API. Not required, default is
                https://secure.actblue.com/api/v1. You can set an ``ACTBLUE_URI`` env variable or
                use this URI parameter if a different endpoint is necessary - for example, when
                running this code in a test environment where you don't want to hit the actual API.

        For instructions on how to generate a Client UUID and Client Secret set,
        visit https://secure.actblue.com/docs/csv_api#authentication.
    """

    def __init__(self, actblue_client_uuid=None, actblue_client_secret=None, actblue_uri=None):
        self.actblue_client_uuid = check_env.check("ACTBLUE_CLIENT_UUID", actblue_client_uuid)
        self.actblue_client_secret = check_env.check("ACTBLUE_CLIENT_SECRET", actblue_client_secret)
        self.uri = (
            check_env.check("ACTBLUE_URI", actblue_uri, optional=True) or ACTBLUE_API_ENDPOINT
        )
        self.headers = {
            "accept": "application/json",
        }
        self.client = APIConnector(
            self.uri,
            auth=(self.actblue_client_uuid, self.actblue_client_secret),
            headers=self.headers,
        )

    def post_request(self, csv_type=None, date_range_start=None, date_range_end=None):
        """
        POST request to ActBlue API to begin generating the CSV.

        `Args:`
            csv_type: str
                Type of CSV you are requesting.
                Options:
                    'paid_contributions': contains paid, non-refunded contributions to the entity
                    (campaign or organization) you created the credential for, during the specified
                    date range.

                    'refunded_contributions': contributions to your entity that were refunded,
                    during the specified date range.

                    'managed_form_contributions': contributions made through any form that is
                    managed by your entity, during the specified date range - including
                    contributions to other entities via that form if it is a tandem form.
            date_range_start: str
                Start of date range to withdraw contribution data (inclusive). Ex: '2020-01-01'
            date_range_end: str
                End of date range to withdraw contribution data (exclusive). Ex: '2020-02-01'

        `Returns:`
            Response of POST request; a successful response includes 'id', a unique identifier for
            the CSV being generated.
        """

        body = {
            "csv_type": csv_type,
            "date_range_start": date_range_start,
            "date_range_end": date_range_end,
        }
        logger.info(f"Requesting {csv_type} from {date_range_start} up to {date_range_end}.")
        response = self.client.post_request(url="csvs", json=body)
        return response

    def get_download_url(self, csv_id=None):
        """
        GET request to retrieve download_url for generated CSV.

        `Args:`
            csv_id: str
                Unique identifier of the CSV you requested.

        `Returns:`
            While CSV is being generated, 'None' is returned. When CSV is ready, the method returns
            the download_url.
        """
        response = self.client.get_request(url=f"csvs/{csv_id}")

        return response["download_url"]

    def poll_for_download_url(self, csv_id):
        """
        Poll the GET request method to check whether CSV generation has finished, signified by the
        presence of a download_url.

        `Args:`
            csv_id: str
                Unique identifier of the CSV you requested.

        `Returns:`
            Download URL from which you can download the generated CSV, valid for 10 minutes after
            retrieval. Null until CSV has finished generating. Keep this URL secure because until
            it expires, it could be used by anyone to download the CSV.
        """

        logger.info("Request received. Please wait while ActBlue generates this data.")
        download_url = None
        while download_url is None:
            download_url = self.get_download_url(csv_id)
            time.sleep(POLLING_DELAY)

        logger.info("Completed data generation.")
        logger.info("Beginning conversion to Parsons Table.")
        return download_url

    def get_contributions(self, csv_type, date_range_start, date_range_end):
        """
        Get specified contribution data from CSV API as Parsons table.

        `Args:`
            csv_type: str
                Type of CSV you are requesting.
                Options:
                    'paid_contributions': contains paid, non-refunded contributions to the entity
                    (campaign or organization) you created the credential for, during the specified
                    date range.

                    'refunded_contributions': contributions to your entity that were refunded,
                    during the specified date range.

                    'managed_form_contributions': contributions made through any form that is
                    managed by your entity, during the specified date range - including
                    contributions to other entities via that form if it is a tandem form.
            date_range_start: str
                Start of date range to withdraw contribution data (inclusive). Ex: '2020-01-01'
            date_range_end: str
                End of date range to withdraw contribution data (exclusive). Ex: '2020-02-01'

        `Returns:`
            Contents of the generated contribution CSV as a Parsons table.
        """

        post_request_response = self.post_request(csv_type, date_range_start, date_range_end)
        csv_id = post_request_response["id"]
        download_url = self.poll_for_download_url(csv_id)
        table = Table.from_csv(download_url)
        logger.info("Completed conversion to Parsons Table.")
        return table
