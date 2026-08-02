import logging
from datetime import datetime
from typing import Any

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)

DonationChargeData = dict[str, int | str | bool | dict | dict[str, Any]]
DonationChargeMetadata = dict[str, int]


class SolidarityTechDonationCharges(SolidarityTechBase):
    def get_donation_charges(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> tuple[Table, DonationChargeMetadata]:
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

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

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

        expected_responses = {200: (True, "donation charges listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[DonationChargeData] = res.json()["data"]
        meta: DonationChargeMetadata = res.json()["meta"]

        return Table(data), meta

    def get_donation_charge(
        self,
        id: int,
    ) -> DonationChargeData:
        """
        Retrieve a single donation charge.

        Args:
            id:
                ID of the donation charge to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single donation charge entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_donation-charges-id>`__

        """
        res = self._get_single_resource("donation_charges", id)

        expected_responses = {404: (False, "donation charge not found")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()
