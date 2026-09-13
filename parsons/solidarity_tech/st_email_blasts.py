"""Connector class for interacting with the SolidarityTech Email Blasts endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import EmailBlastData, Metadata

logger = logging.getLogger(__name__)


class SolidarityTechEmailBlasts(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech email blasts endpoint."""

    def get_email_blasts(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> tuple[Table, Metadata]:
        """
        Retrieve a list of email blasts.

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
            All the email blasts.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_email-blasts>`__

        """
        res = self._get_resources(
            "email_blasts",
            limit=limit,
            offset=offset,
            since=since,
        )

        expected_responses = {HTTPStatus.OK: (True, "email blasts listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[EmailBlastData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Email Blasts"), meta

    def get_email_blast(
        self,
        resource_id: int,
    ) -> tuple[EmailBlastData, Metadata]:
        """
        Retrieve a single email blast.

        Args:
            resource_id:
                ID of the email blast to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single email blast entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_email-blasts-id>`__

        """
        res = self._get_single_resource("email_blasts", resource_id)

        expected_responses = {
            HTTPStatus.OK: (True, "email blast found"),
            HTTPStatus.UNPROCESSABLE_ENTITY: (False, "email blast not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: EmailBlastData = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return data, meta
