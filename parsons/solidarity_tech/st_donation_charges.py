import logging
from datetime import datetime

from requests.exceptions import HTTPError

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechDonationCharges(SolidarityTechBase):
    def get_donation_charges(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime | None = 0,
    ) -> str:
        """
        Retrieve a list of donation charges.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.

        Returns:
            All the donation charges.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_donation-charges>`__

        """
        res = self._get_resources(
            "donation_charges",
            limit=limit,
            offset=offset,
            since=since,
            additional_headers={"accept": "application/json"},
        )

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_donation_charge(
        self,
        id: int,
    ) -> str:
        """
        Retrieve a single donation charge.

        Args:
            id:
                ID of the donation charge to retrieve.

        Returns:
            A single agent assignment entry.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_donation-charges-id>`__

        """
        res = self._get_single_resource("donation_charges", id)

        if res.status_code == 404:
            raise HTTPError("Donation charge not found")

        if res.status_code:
            raise STUnexpectedResponseCodeError(res)

        return res.text
