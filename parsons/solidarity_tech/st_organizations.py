from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

logger = logging.getLogger(__name__)


class SolidarityTechOrganizations(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech organizations API."""

    def get_organizations(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> Table:
        """
        Retrieve a list of organizations.

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
            All the organizations.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_organizations>`__

        """
        res = self._get_resources(
            "organizations",
            limit=limit,
            offset=offset,
            since=since,
        )

        expected_responses = {200: (True, "organizations listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_organization(
        self,
        id: int,
    ) -> dict:
        """
        Retrieve a single organization.

        Args:
            id:
                ID of the organization to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single organization entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_organizations-id>`__

        """
        res = self._get_single_resource("organizations", id)

        expected_responses = {
            200: (True, "organization found"),
            404: (False, "organization not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()
