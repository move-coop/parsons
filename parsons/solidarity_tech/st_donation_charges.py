"""Connector class for interacting with the SolidarityTech Donation Charges endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import DonationChargeData, Metadata

logger = logging.getLogger(__name__)


class SolidarityTechDonationCharges(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech donation charges endpoint."""

    def get_donation_charges(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> tuple[Table, Metadata]:
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

        expected_responses = {HTTPStatus.OK: (True, "donation charges listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[DonationChargeData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Donation Charges"), meta

    def get_donation_charge(
        self,
        resource_id: int,
    ) -> tuple[DonationChargeData, Metadata]:
        """
        Retrieve a single donation charge.

        Args:
            resource_id:
                ID of the donation charge to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single donation charge entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_donation-charges-id>`__

        """
        res = self._get_single_resource("donation_charges", resource_id)

        expected_responses = {
            HTTPStatus.OK: (True, "donation charge retrieved"),
            HTTPStatus.NOT_FOUND: (False, "donation charge not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: DonationChargeData = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return data, meta
