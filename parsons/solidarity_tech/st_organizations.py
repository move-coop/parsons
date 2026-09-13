"""Connector class for interacting with the SolidarityTech Organizations endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import Metadata, OrganizationData

logger = logging.getLogger(__name__)


class SolidarityTechOrganizations(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech organizations endpoint."""

    def get_organizations(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> tuple[Table, Metadata]:
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

        expected_responses = {HTTPStatus.OK: (True, "organizations listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[OrganizationData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Organizations"), meta

    def get_organization(
        self,
        resource_id: int,
    ) -> tuple[OrganizationData, Metadata]:
        """
        Retrieve a single organization.

        Args:
            resource_id:
                ID of the organization to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single organization entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_organizations-id>`__

        """
        res = self._get_single_resource("organizations", resource_id)

        expected_responses = {
            HTTPStatus.OK: (True, "organization found"),
            HTTPStatus.NOT_FOUND: (False, "organization not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: OrganizationData = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return data, meta
