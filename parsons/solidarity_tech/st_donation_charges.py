from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, TypedDict

from parsons import Table
from parsons.solidarity_tech.base import Metadata, SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

logger = logging.getLogger(__name__)


class DonationChargeDataChapter(TypedDict):
    id: int
    name: str


class DonationChargeDataUser(TypedDict):
    id: int
    email: str
    first_name: str
    last_name: str
    phone_number: str
    created_at: str
    address1: str | None
    address2: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    country_name: str | None


class DonationChargeDataActionPage(TypedDict):
    id: int
    title: str
    url_slug: str


class DonationChargeData(TypedDict):
    id: int
    amount: int
    created_at: str
    updated_at: str
    success: bool
    refunded: bool
    receipt_number: str
    hash_id: str
    processing_fee_cents: int | None
    external_donation_id: str | None
    external_donation_date: str | None
    is_external: bool
    amount_in_dollars: str
    currency: str
    currency_symbol: str
    receipt_url: str
    brand: str
    last4: str
    json: dict[str, Any]
    user: DonationChargeDataUser
    action_page: DonationChargeDataActionPage
    chapter: DonationChargeDataChapter


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

        expected_responses = {200: (True, "donation charges listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[DonationChargeData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data), meta

    def get_donation_charge(
        self,
        resource_id: int,
    ) -> DonationChargeData:
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

        expected_responses = {404: (False, "donation charge not found")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()
