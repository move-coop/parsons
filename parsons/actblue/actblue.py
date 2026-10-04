import logging
import time
from typing import Literal, cast

from requests.auth import HTTPBasicAuth

from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector, _JsonType

logger = logging.getLogger(__name__)

POLLING_DELAY = 1
ACTBLUE_API_ENDPOINT = "https://secure.actblue.com/api/v1"


class ActBlue:
    """Parsons connector for interacting with ActBlue endpoints."""

    def __init__(
        self,
        actblue_client_uuid: str | None = None,
        actblue_client_secret: str | None = None,
        actblue_uri: str | None = None,
        max_retries: int | None = None,
    ) -> None:
        """
        Instantiate the ActBlue class.

        .. admonition:: Generating a Client UUID and Client Secret

            See https://secure.actblue.com/docs/csv_api#authentication.

        Args:
            actblue_client_uuid:
                The ActBlue provided Client UUID.
                Not required if ``ACTBLUE_CLIENT_UUID`` env variable set.
            actblue_client_secret:
                The ActBlue provided Client Secret.
                Not required if ``ACTBLUE_CLIENT_SECRET`` env variable set.
            actblue_uri:
                The URI to access the CSV API if a different endpoint is necessary.
                Not required. Default is `https://secure.actblue.com/api/v1`.
                If not provided via this parameter, can be set by ``ACTBLUE_URI`` env variable.
                Useful when running this code in a test environment where you don't want to hit the actual API.
            max_retries:
                The maximum number of times to poll the API for a download URL.
                Not required. Default is None, which means it will poll indefinitely until a download URL is returned.
                If not provided via this parameter, can be set by ``ACTBLUE_MAX_RETRIES`` env variable.

        """
        self.actblue_client_uuid = check_env.check("ACTBLUE_CLIENT_UUID", actblue_client_uuid)
        self.actblue_client_secret = check_env.check("ACTBLUE_CLIENT_SECRET", actblue_client_secret)
        self.uri = (
            check_env.check("ACTBLUE_URI", actblue_uri, optional=True) or ACTBLUE_API_ENDPOINT
        )
        self.headers = {"accept": "application/json"}
        auth = HTTPBasicAuth(self.actblue_client_uuid, self.actblue_client_secret)
        self.client = APIConnector(self.uri, auth=auth, headers=self.headers)
        self.max_retries = (
            int(val)
            if (val := check_env.check("ACTBLUE_MAX_RETRIES", max_retries, optional=True))
            else None
        )

    def post_request(
        self,
        csv_type: Literal[
            "paid_contributions", "refunded_contributions", "managed_form_contributions"
        ]
        | None = None,
        date_range_start: str | None = None,
        date_range_end: str | None = None,
    ) -> _JsonType:
        """
        POST request to ActBlue API to begin generating the CSV.

        Args:
            csv_type:
                Type of CSV you are requesting.
                Options:

                - 'paid_contributions': contains paid, non-refunded contributions to the entity
                  (campaign or organization) you created the credential for, during the specified
                  date range.
                - 'refunded_contributions': contributions to your entity that were refunded,
                  during the specified date range.
                - 'managed_form_contributions': contributions made through any form that is
                   managed by your entity, during the specified date range - including
                   contributions to other entities via that form if it is a tandem form.

            date_range_start:
                Start of date range to withdraw contribution data (inclusive). Ex: '2020-01-01'
            date_range_end:
                End of date range to withdraw contribution data (exclusive). Ex: '2020-02-01'

        Returns:
            Json data returned from POST request.
            A successful response includes 'id',
            a unique identifier for the CSV being generated.

        """
        body = {
            "csv_type": csv_type,
            "date_range_start": date_range_start,
            "date_range_end": date_range_end,
        }
        logger.info("Requesting %s from %s up to %s.", csv_type, date_range_start, date_range_end)
        return self.client.post_request(url="csvs", json=body)

    def get_download_url(self, csv_id: str | None = None) -> str | None:
        """
        GET request to retrieve download_url for generated CSV.

        Args:
            csv_id: Unique identifier of the CSV you requested.

        Returns:
            While CSV is being generated, 'None' is returned. When CSV is ready, the method returns
            the download_url.

        """
        response = cast("dict[str, str]", self.client.get_request(url=f"csvs/{csv_id}"))
        in_progress = response.get("status") == "in_progress"
        if (url := response.get("download_url")) is None and not in_progress:
            err_msg = "CSV generation failed: %s"
            raise ValueError(err_msg, response)

        return url

    def poll_for_download_url(self, csv_id: str) -> str:
        """
        Poll the GET request method to check whether CSV generation has finished.

        Success is signified by the presence of a ``download_url``.

        Args:
            csv_id: Unique identifier of the CSV you requested.

        Returns:
            Download URL from which you can download the generated CSV.
            URL is valid for 10 minutes after retrieval.
            None is returned until CSV has finished generating.
            Keep this URL secure, because (until it expires) it could be used by anyone to download the CSV.

        """
        logger.info("Request received. Please wait while ActBlue generates this data.")
        download_url = None
        tries = 0
        while download_url is None and (self.max_retries is None or tries < self.max_retries):
            download_url = self.get_download_url(csv_id)
            time.sleep(POLLING_DELAY)
            tries += 1

        if download_url is None:
            err_msg = "CSV generation timed out. Increase max_retries and try again."
            raise TimeoutError(err_msg)

        logger.info("Completed data generation.")
        logger.info("Beginning conversion to Parsons Table.")
        return download_url

    def get_contributions(
        self,
        csv_type: Literal[
            "paid_contributions", "refunded_contributions", "managed_form_contributions"
        ],
        date_range_start: str,
        date_range_end: str,
        **csvargs,
    ) -> Table:
        """
        Get specified contribution data from CSV API as Parsons table.

        Args:
            csv_type:
                Type of CSV you are requesting.
                Options:

                - 'paid_contributions': contains paid, non-refunded contributions to the entity
                  (campaign or organization) you created the credential for, during the specified
                  date range.
                - 'refunded_contributions': contributions to your entity that were refunded,
                  during the specified date range.
                - 'managed_form_contributions': contributions made through any form that is
                   managed by your entity, during the specified date range - including
                   contributions to other entities via that form if it is a tandem form.

            date_range_start:
                Start of date range to withdraw contribution data (inclusive). Ex: '2020-01-01'
            date_range_end:
                End of date range to withdraw contribution data (exclusive). Ex: '2020-02-01'
            `**csvargs`:
                Any additional arguments will be passed to Table.from_csv as keyword arguments.

        Returns:
            Table
                Contents of the generated contribution CSV.
                List of columns:

                - Receipt ID
                - Date
                - Amount
                - Recurring Total Months
                - Recurrence Number
                - Recipient
                - Fundraising Page
                - Fundraising Partner
                - Reference Code 2
                - Reference Code
                - Donor First Name
                - Donor Last Name
                - Donor Addr1
                - Donor Addr2
                - Donor City
                - Donor State
                - Donor ZIP
                - Donor Country
                - Donor Occupation
                - Donor Employer
                - Donor Email
                - Donor Phone
                - New Express Signup
                - Comments
                - Check Number
                - Check Date
                - Employer Addr1
                - Employer Addr2
                - Employer City
                - Employer State
                - Employer ZIP
                - Employer Country
                - Donor ID
                - Fundraiser ID
                - Fundraiser Recipient ID
                - Fundraiser Contact Email
                - Fundraiser Contact First Name
                - Fundraiser Contact Last Name
                - Partner ID
                - Partner Contact Email
                - Partner Contact First Name
                - Partner Contact Last Name
                - Reserved
                - Lineitem ID
                - AB Test Name
                - AB Variation
                - Recipient Committee
                - Recipient ID
                - Recipient Gov ID
                - Recipient Election
                - Reserved
                - Payment ID
                - Payment Date
                - Disbursement ID
                - Disbursement Date
                - Recovery ID
                - Recovery Date
                - Refund ID
                - Refund Date
                - Fee
                - Recur Weekly
                - ActBlue Express Lane
                - Reserved
                - Card Type
                - Reserved
                - Mobile
                - Recurring Upsell Shown
                - Recurring Upsell Succeeded
                - Double Down
                - Smart Recurring
                - Monthly Recurring Amount
                - Apple Pay
                - Card Replaced by Account Updater
                - ActBlue Express Donor
                - Custom Field 1 Label
                - Custom Field 1 Value
                - Donor US Passport Number
                - Text Message Opt In
                - Gift Identifier
                - Gift Declined
                - Shipping Addr1
                - Shipping City
                - Shipping State
                - Shipping Zip
                - Shipping Country
                - Weekly Recurring Amount
                - Smart Boost Amount
                - Smart Boost Shown
                - Bump Recurring Seen
                - Bump Recurring Succeeded
                - Weekly to Monthly Rollover Date
                - Weekly Recurring Sunset
                - Recurring Type
                - Recurring Pledged
                - Paypal
                - Kind
                - Managed Entity Name
                - Managed Entity Committee Name

        """
        post_request_response = self.post_request(csv_type, date_range_start, date_range_end)
        csv_id = post_request_response["id"]
        download_url = self.poll_for_download_url(csv_id)
        table = Table.from_csv(download_url, **csvargs)
        logger.info("Completed conversion to Parsons Table.")
        return table
