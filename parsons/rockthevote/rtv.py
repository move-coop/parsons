import datetime
import logging
import petl
import re
import requests
import time

from dateutil.parser import parse as parse_date

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)


VALID_REPORT_TYPES = ["extended"]
TESTING_URI = "https://staging.rocky.rockthevote.com/api/v4"
PRODUCTION_URI = "https://register.rockthevote.com/api/v4"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S UTC"
"""Datetime format for sending date's to the API."""

REQUEST_HEADERS = {
    # For some reason, RTV's firewall REALLY doesn't like the
    # user-agent string that Python's request library gives by default,
    # though it seems fine with the curl user agent
    # For more info on user agents, see:
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
    "user-agent": "curl/7.54.0"
}
"""Standard request header for sending requests to the API."""

STATUS_URL_PARSE_REGEX = re.compile(r"(\d+)$")
"""Regex for parsing the report ID from the status URL."""


class RTVFailure(Exception):
    """Exception raised when there is an error with the connector."""


class RockTheVote:
    """
    Instantiate the RockTheVote class

    `Args:`
        partner_id: str
            The RockTheVote partner ID for the RTV account.
            Not required if the ``RTV_PARTNER_ID`` environmental variable is set.
        partner_api_key: str
            The API Key for the partner.
            Not required if the ``RTV_PARTNER_API_KEY`` environmental variable is set.
        testing: bool
            Whether or not to use the staging instance. Defaults to False.
    `Returns`:
        RockTheVote class
    """

    def __init__(self, partner_id=None, partner_api_key=None, testing=False):
        self.partner_id = check_env.check("RTV_PARTNER_ID", partner_id)
        self.partner_api_key = check_env.check("RTV_PARTNER_API_KEY", partner_api_key)

        if testing:
            self.client = APIConnector(TESTING_URI, headers=REQUEST_HEADERS)
        else:
            self.client = APIConnector(PRODUCTION_URI, headers=REQUEST_HEADERS)

    def create_registration_report(self, before=None, since=None, report_type=None):
        """
        Create a new registration report.

        `Args:`
            before: str
                Limit to registrations that were started before this date, in
                ISO format (e.g. 2020-01-01)
            since: str
                Limit to registrations that were started since this date, in
                ISO format (e.g. 2020-01-01)
            report_type: str
                The type of report to create. If left as None, it creates the default report. The
                ``extended`` report includes additional fields. Currently only accepts ``extended``.
        `Returns:`
            int
                The ID of the created report.
        """
        report_url = "registrant_reports.json"
        # Create the report for the new data
        report_parameters = {
            "partner_id": self.partner_id,
            "partner_API_key": self.partner_api_key,
        }

        # Declare these here so the logging doesn't error out
        since_date = before_date = None

        if report_type:
            if report_type not in VALID_REPORT_TYPES:
                raise RTVFailure(f"Invalid report type. Must be one of {VALID_REPORT_TYPES}")
            report_parameters["report_type"] = report_type
        if since:
            since_date = parse_date(since).strftime(DATETIME_FORMAT)
            report_parameters["since"] = since_date
        if before:
            before_date = parse_date(before).strftime(DATETIME_FORMAT)
            report_parameters["before"] = before_date

        # The report parameters get passed into the request as JSON in the body
        # of the request.
        report_str = f"{report_type} report" if report_type else "report"
        logger.info(
            f"Creating {report_str} for {self.partner_id} "
            f"for dates: {since_date} to {before_date}..."
        )
        response = self.client.request(report_url, "post", json=report_parameters)
        if response.status_code != requests.codes.ok:
            raise RTVFailure("Couldn't create RTV registrations report")

        response_json = response.json()
        # The RTV API says the response should include the report_id, but I have not found
        # that to be the case
        report_id = response_json.get("report_id")
        if report_id:
            logger.info(f"Created report with id {report_id}.")
            return report_id

        # If the response didn't include the report_id, then we will parse it out of the URL.
        status_url = response_json.get("status_url")
        url_match = STATUS_URL_PARSE_REGEX.search(status_url)
        if url_match:
            report_id = url_match.group(1)

        logger.info(f"Created report with id {report_id}.")
        return report_id

    def get_registration_report(
        self,
        report_id,
        block=False,
        poll_interval_seconds=60,
        report_timeout_seconds=3600,
    ):
        """
        Get data from an existing registration report.

        `Args:`
            report_id: int
                The ID of the report to get data from
            block: bool
                Whether or not to block execution until the report is complete
            poll_interval_seconds: int
                If blocking, how long to pause between attempts to check if the report is done
            report_timeout_seconds: int
                If blocking, how long to wait for the report before timing out
        `Returns:`
            Parsons Table
                Parsons table with the report data.
        """
        logger.info(f"Getting report with id {report_id}...")
        credentials = {
            "partner_id": self.partner_id,
            "partner_API_key": self.partner_api_key,
        }
        status_url = f"registrant_reports/{report_id}"
        download_url = None

        # Let's figure out at what time should we just give up because we waited
        # too long
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=report_timeout_seconds)

        # If we have a download URL, we can move on and just download the
        # report. Otherwise, as long as we haven't run out of time, we will
        # check the status.
        while not download_url and datetime.datetime.now() < end_time:
            logger.debug(
                f"Registrations report not ready yet, sleeping {poll_interval_seconds} seconds"
            )

            # Check the status again via the status endpoint
            status_response = self.client.request(status_url, "get", params=credentials)

            # Check to make sure the call got a valid response
            if status_response.status_code == requests.codes.ok:
                status_json = status_response.json()

                # Grab the download_url from the response.
                download_url = status_json.get("download_url")

                if not download_url and not block:
                    return None
            else:
                raise RTVFailure("Couldn't get report status")

            if not download_url:
                # We just got the status, so we should wait a minute before
                # we check it again.
                time.sleep(poll_interval_seconds)

        # If we never got a valid download_url, then we timed out waiting for
        # the report to generate. We will log an error and exit.
        if not download_url:
            raise RTVFailure("Timed out waiting for report")

        # Download the report data
        download_response = self.client.request(download_url, "get", params=credentials)

        # Check to make sure the call got a valid response
        if download_response.status_code == requests.codes.ok:
            report_data = download_response.text

            # Load the report data into a Parsons Table
            table = Table.from_csv_string(report_data)

            # Transform the data from the report's CSV format to something more
            # Pythonic (snake case)
            normalized_column_names = [re.sub(r"\s", "_", name).lower() for name in table.columns]
            normalized_column_names = [
                re.sub(r"[^A-Za-z\d_]", "", name) for name in normalized_column_names
            ]
            table.table = petl.setheader(table.table, normalized_column_names)
            return table
        else:
            raise RTVFailure("Unable to download report data")

    def run_registration_report(
        self,
        before=None,
        since=None,
        report_type=None,
        poll_interval_seconds=60,
        report_timeout_seconds=3600,
    ):
        """
        Run a new registration report.

        This method will block until the report has finished generating, or until the specified
        timeout is reached.

        `Args:`
            before: str
                Limit to registrations that were started before this date, in
                ISO format (e.g. 2020-01-01)
            since: str
                Limit to registrations that were started since this date, in
                ISO format (e.g. 2020-01-01)
            report_type: str
                The type of report to run. If left as None, it runs the default report. The
                ``extended`` report includes additional fields. Currently only accepts ``extended``.
            poll_interval_seconds: int
                If blocking, how long to pause between attempts to check if the report is done
            report_timeout_seconds: int
                If blocking, how long to wait for the report before timing out
        `Returns:`
            Parsons.Table
                The table with the report data.
        """
        report_str = f"{report_type} report" if report_type else "report"
        logger.info(
            f"Running {report_str} for {self.partner_id} " f"for dates: {since} to {before}..."
        )
        report_id = self.create_registration_report(
            before=before, since=since, report_type=report_type
        )
        return self.get_registration_report(
            report_id,
            block=True,
            poll_interval_seconds=poll_interval_seconds,
            report_timeout_seconds=report_timeout_seconds,
        )

    def get_state_requirements(
        self, lang, home_state_id, home_zip_code, date_of_birth=None, callback=None
    ):
        """
        Checks state eligibility and provides state specific fields information.
        Args:
            lang: str
                Required. Language. Represented by an abbreviation. 'en', 'es', etc
            home_state_id: str
                Required. 2-character state abbreviation
            home_zip_code: str
                Required. 'zzzzz' 5 digit zip codes
            date_of_birth: str
                Optional. 'mm-dd-yyyy'
            callback: str
                Optional.  If used, will change the return value from JSON format to jsonp
        Returns:
            Parsons.Table
                A single row table with the response json
        """
        requirements_url = "state_requirements.json"

        logger.info(f"Getting the requirements for {home_state_id}...")

        params = {
            "lang": lang,
            "home_state_id": home_state_id,
            "home_zip_code": home_zip_code,
        }

        if date_of_birth:
            params["date_of_birth"] = date_of_birth

        if callback:
            params["callback"] = callback

        requirements_response = self.client.request(requirements_url, "get", params=params)

        if requirements_response.status_code == requests.codes.ok:
            response_json = requirements_response.json()
            table = Table([response_json])
            return table
        else:
            error_json = requirements_response.json()
            logger.info(f"{error_json}")
            raise RTVFailure("Could not retrieve state requirements")
