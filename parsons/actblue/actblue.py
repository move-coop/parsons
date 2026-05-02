import itertools
import logging
import time
from datetime import date
from typing import Any, Literal, NoReturn

from requests.auth import HTTPBasicAuth

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons.utilities.datetime import convert_date_to_simple

logger = logging.getLogger(__name__)

POLLING_DELAY = 1
ACTBLUE_API_ENDPOINT = "https://secure.actblue.com/api/v1"

CSVType = Literal["paid_contributions", "refunded_contributions", "managed_form_contributions"]


class ActBlue:
    """
    Instantiate class.

    For instructions on how to generate a Client UUID and Client Secret set,
    visit the `ActBlue CSV API Authentication Documentation`_.

    Args:
        actblue_client_uuid:
            The ActBlue provided Client UUID.
            Not required if ``ACTBLUE_CLIENT_UUID`` env variable is set.
        actblue_client_secret:
            The ActBlue provided Client Secret.
            Not required if ``ACTBLUE_CLIENT_SECRET`` env variable is set.
        actblue_uri:
            The URI to access the CSV API.
            Alternately, ``ACTBLUE_URI`` env variable can be set.
            For example, when running this code in a test environment
            where you don't want to hit the actual API.
            Default is ``https://secure.actblue.com/api/v1``.
        max_retries:
            The maximum number of times to poll the API for a download URL.
            Alternately, ``ACTBLUE_MAX_RETRIES`` env variable can be set.
            If ``None``, it will poll indefinitely until a download URL is returned.
            Default is ``None``.

    """

    def __init__(
        self,
        actblue_client_uuid: str | None = None,
        actblue_client_secret: str | None = None,
        actblue_uri: str | None = None,
        max_retries: int | None = None,
    ) -> None:
        self.actblue_client_uuid: str = check_env.check("ACTBLUE_CLIENT_UUID", actblue_client_uuid)
        self.actblue_client_secret: str = check_env.check(
            "ACTBLUE_CLIENT_SECRET", actblue_client_secret
        )
        self.uri = (
            check_env.check("ACTBLUE_URI", actblue_uri, optional=True) or ACTBLUE_API_ENDPOINT
        )
        self.headers = {
            "accept": "application/json",
        }
        self.client = APIConnector(
            self.uri,
            auth=HTTPBasicAuth(self.actblue_client_uuid, self.actblue_client_secret),
            headers=self.headers,
        )
        self.max_retries = check_env.check("ACTBLUE_MAX_RETRIES", max_retries, optional=True)
        self.max_retries = int(self.max_retries) if self.max_retries else None

    def post_request(
        self,
        csv_type: CSVType | None = None,
        date_range_start: date | str | None = None,
        date_range_end: date | str | None = None,
    ) -> dict[str, Any] | int | None:
        """
        POST request to ActBlue API to begin generating the CSV.

        Args:
            csv_type:
                Type of CSV you are requesting.

                - 'paid_contributions': Contributions to the entity (campaign or organization)
                   you created the credential for that have not been refunded.
                - 'refunded_contributions': Contributions to the entity that were refunded.
                - 'managed_form_contributions': Contributions made through any form that is
                   managed by the entity. Includes contributions to other entities on tandem forms.

            date_range_start:
                Start of date range to withdraw contribution data (inclusive).
                Ex: ``2020-01-01``.
            date_range_end:
                End of date range to withdraw contribution data (exclusive).
                Ex: ``2020-02-01``.

        Returns:
            Response of POST request.
            A successful response includes 'id', a unique identifier for the CSV being generated.

        """
        body = {
            "csv_type": csv_type,
            "date_range_start": convert_date_to_simple(date_range_start),
            "date_range_end": convert_date_to_simple(date_range_end),
        }
        logger.info(
            "Requesting %s from %s up to %s.",
            body["csv_type"],
            body["date_range_start"],
            body["date_range_end"],
        )
        response = self.client.post_request(url="csvs", json=body)

        return response

    def get_download_url(self, csv_id: str | None = None) -> str | None:
        """
        GET request to retrieve download_url for generated CSV.

        Args:
            csv_id: Unique identifier of the CSV you requested.

        Returns:
            While CSV is being generated, 'None' is returned. When CSV is ready, the method returns
            the download_url.

        """
        response = self.client.get_request(url=f"csvs/{csv_id}")
        if response.get("download_url") is None and response.get("status") != "in_progress":
            raise ValueError("CSV generation failed: %s", response)

        return response["download_url"]

    def poll_for_download_url(self, csv_id: str) -> str | NoReturn:
        """
        Poll the GET request method to check whether CSV generation has finished.

        Completion is signified by the presence of a ``download_url`` key.

        Args:
            csv_id: Unique identifier of the CSV you requested.

        Returns:
            Download URL from which you can download the generated CSV, valid for 10 minutes after
            retrieval. Null until CSV has finished generating. Keep this URL secure because until
            it expires, it could be used by anyone to download the CSV.

        Raises:
            TimeoutError: If the CSV generation times out.

        """
        logger.info("Request received. Please wait while ActBlue generates this data.")
        download_url = None
        attempts = itertools.count() if self.max_retries is None else range(self.max_retries)
        for _ in attempts:
            download_url = self.get_download_url(csv_id)
            if download_url is not None:
                logger.info("Completed data generation.")
                break

            time.sleep(POLLING_DELAY)

        if download_url is None:
            raise TimeoutError("CSV generation timed out. Increase max_retries and try again.")

        return download_url

    def get_contributions(
        self,
        csv_type: CSVType,
        date_range_start: date | str | None = None,
        date_range_end: date | str | None = None,
        **csvargs,
    ) -> Table:
        """
        Get specified contribution data from CSV API as Parsons table.

        Args:
            csv_type:
                Type of CSV you are requesting.
                Options:

                - 'paid_contributions': Contributions to the entity (campaign or organization)
                   you created the credential for that have not been refunded.
                - 'refunded_contributions': Contributions to the entity that were refunded.
                - 'managed_form_contributions': Contributions made through any form that is
                   managed by the entity. Includes contributions to other entities on tandem forms.

            date_range_start:
                Start of date range to withdraw contribution data (inclusive).
                Ex: ``2020-01-01``.
            date_range_end:
                End of date range to withdraw contribution data (exclusive).
                Ex: ``2020-02-01``.
            `**csvargs`:
                Any additional arguments will be passed to
                :meth:`parsons.etl.table.Table.from_csv` as keyword arguments.

        Returns:
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
        post_request_response: dict[str, Any] = self.post_request(
            csv_type,
            convert_date_to_simple(date_range_start),
            convert_date_to_simple(date_range_end),
        )
        csv_id = post_request_response["id"]
        download_url = self.poll_for_download_url(csv_id)
        table = Table.from_csv(download_url, **csvargs)
        logger.info("Completed conversion to Parsons Table.")

        return table
