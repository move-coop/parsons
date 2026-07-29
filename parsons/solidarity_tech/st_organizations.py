import logging
from datetime import datetime

from requests import HTTPError

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechOrganizations(SolidarityTechBase):
    def get_organizations(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime | None = 0,
    ) -> str:
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

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_organization(
        self,
        id: int,
    ) -> str:
        """
        Retrieve a single organization.

        Args:
            id:
                ID of the organization to retrieve.

        Returns:
            A single organization entry.

        Raises:
            HTTPError: If the organization is not found.
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_organizations-id>`__

        """
        res = self._get_single_resource("organizations", id)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 404:
            raise HTTPError("Organization not found.", response=res)

        return res.text
