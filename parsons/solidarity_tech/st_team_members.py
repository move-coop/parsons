import logging
from datetime import datetime

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase
from parsons.solidarity_tech.solidarity_tech_literals import InviteType, ScopeType

logger = logging.getLogger(__name__)


class SolidarityTechTeamMembers(SolidarityTechBase):
    def get_team_members(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> Table:
        """
        Retrieve a list of team members.

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
            All the team member entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_task-assignments-id>`__

        """
        res = self._get_resources(
            "team_members",
            limit=limit,
            offset=offset,
            since=since,
        )

        expected_responses = {200: (True, "team members listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def create_team_member(
        self,
        role_id: int,
        scope_type: ScopeType,
        scope_id: int,
        invite_via: InviteType,
        member_id: str | None = None,
        phone_number: str | None = None,
        email: str | None = None,
        full_name: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        task_id: int | None = None,
    ) -> bool:
        """
        Create a new team member.

        Args:
            member_id:
                Hash ID of existing user (optional if phone_number or email provided).
            phone_number:
                Phone number of the person (primary key for user lookup/creation).
            email:
                Email of the person (secondary key for user lookup/creation).
            full_name:
                Full name for new user creation.
            first_name:
                First name for new user creation.
            last_name:
                Last name for new user creation.
            role_id:
                ID of the role to assign.
            scope_type:
                Type of scope.
            scope_id:
                ID of the scope (Chapter or Organization).
            invite_via:
                How to send the invitation.
            task_id:
                Optional task ID to assign the member to.

        Raises:
            :class:`ValueError`: If none of ``member_id``, ``phone_number`` or ``email`` is provided.
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_task-assignments-id>`__

        """
        if not member_id and not phone_number and not email:
            raise ValueError("One of member_id, phone_number, or email is required.")

        payload = {
            "member_id": member_id,
            "phone_number": phone_number,
            "email": email,
            "full_name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "role_id": role_id,
            "scope_type": scope_type,
            "scope_id": scope_id,
            "invite_via": invite_via,
            "task_id": task_id,
        }
        res = self._post_request(
            "team_members", payload=payload, additional_headers={"content-type": "application/json"}
        )

        expected_responses = {
            201: (True, "team member created"),
            422: (False, "invalid parameters"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def update_team_member(
        self,
        id: int,
        role_id: int,
        scope_type: ScopeType,
        scope_id: int,
    ) -> bool:
        """
        Update a team member with the specified details.

        Args:
            id:
                Team member ID (UserRoleScope ID).
            role_id:
                ID of the role to assign.
            scope_type:
                Type of scope.
            scope_id:
                ID of the scope (Chapter or Organization).

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_task-assignments-id>`__

        """
        payload = {
            "role_id": role_id,
            "scope_type": scope_type,
            "scope_id": scope_id,
        }
        res = self._put_request(
            "team_members",
            id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {200: (True, "team member updated")}
        return self._handle_status_codes(res=res, codes=expected_responses)
