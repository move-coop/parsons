import logging
import numbers
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)

CompareValueType = str | numbers.Rational | bool
QueryParamType = dict[
    str, str | bool | list[dict[str, CompareValueType | list[dict[str, CompareValueType]]]]
]
UserData = dict[str, str | int | list[int] | list[str] | dict[str, Any] | bool]
UserMetadata = dict[str, int]
UserMergeMetadata = dict[str, str | int | list[int]]
UserDeleteMetadata = dict[str, int]


class SolidarityTechUsers(SolidarityTechBase):
    def get_users(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        user_list_ids: str | list[int] | None = None,
        phone_number: str | None = None,
        email: str | None = None,
    ) -> tuple[Table, UserMetadata]:
        """
        Retrieve a list of users.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            user_list_ids:
                Comma-separated list of user list IDs to apply.
                Or a list of user ID integers.
            phone_number:
                Filter by phone number (any format accepted, will be normalized).
            email:
                Filter by email address (case-insensitive).

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the users.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_users>`__

        """
        if isinstance(user_list_ids, list):
            user_list_ids = ",".join(str(id) for id in user_list_ids)

        params = {
            "user_list_ids": user_list_ids,
            "phone_number": phone_number,
            "email": email,
        }
        res = self._get_resources(
            "users",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
            additional_headers={"accept": "application/json"},
        )

        expected_responses = {
            200: (True, "users listed"),
            422: (False, "invalid user filter"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[UserData] = res.json()["data"]
        meta: UserMetadata = res.json()["meta"]

        return Table(data), meta

    def get_user(
        self,
        id: int,
    ) -> UserData:
        """
        Retrieve a single user.

        Args:
            id:
                ID of the user to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single user.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_users-id>`__

        """
        res = self._get_single_resource(
            "users", id, additional_headers={"accept": "application/json"}
        )

        expected_responses = {
            200: (True, "user found"),
            404: (False, "user not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def create_user(
        self,
        phone_number: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        alternate_name: str | None = None,
        preferred_language: str | None = None,
        second_language: str | None = None,
        chapter_id: int | None = None,
        chapter_ids: list[int] | None = None,
        referred_by_user_id: int | None = None,
        custom_user_properties: dict[str, str | list[str]] | None = None,
        append_custom_user_properties: bool = True,
        add_tags: list[str] | None = None,
        remove_tags: list[str] | None = None,
        donation_charge: dict[str, numbers.Number | str] | None = None,
        address: dict[str, str | float] | None = None,
        assessment: str | None = None,
        sms_permission: bool | None = None,
        call_permission: bool | None = None,
        email_permission: bool | None = None,
        timezone: ZoneInfo | str | None = None,
        require_contact_info: bool = True,
        phone_number_textable_validation: bool = True,
        lookup_key: str | None = None,
    ) -> bool:
        """
        Create or update a user with the specified details.

        Args:
            phone_number:
                Phone number of the user.
            email:
                Email address of the user.
            first_name:
                First name of the user.
            last_name:
                Last name of the user.
            alternate_name:
                Alternate name (nickname, community name, or alternate romanization). Searchable.
                Blank values are ignored; an existing alternate name cannot be cleared via the API.
            preferred_language:
                Preferred language of the user.
            second_language:
                Second language of the user.
            chapter_id:
                Primary chapter ID.
                Required for new users unless ``chapter_ids`` is provided.
            chapter_ids:
                Array of chapter IDs for multi-chapter membership.
                First element becomes primary if ``chapter_id`` is not provided.
                Requires multi-chapter feature for more than one chapter.
            referred_by_user_id:
                Identifier for the user who referred this user.
            custom_user_properties:
                Custom property values keyed by ``internal_name``.
                Use a string for single-value fields
                (text, number, radio, dropdown, single checkbox).
                Use an array of strings for Multiple Checkboxes fields
                (e.g. ``["Option A", "Option B"]``).
                Comma-separated strings are also accepted for Multiple Checkboxes
                (e.g. ``"Option A, Option B"``).
                For Multiple Checkboxes, see ``append_custom_user_properties`` to
                control whether values are merged with or replace existing values.
            append_custom_user_properties:
                Controls how Multiple Checkboxes custom properties are written.
                Defaults to True (union new values with existing values, the long-standing API behavior).
                Set to False to overwrite existing values, mirroring bulk update REPLACE mode.
                Has no effect on non-array field types.
            add_tags:
                List of tags to add to the user.
            remove_tags:
                List of tags to remove to the user.
            donation_charge:
                Optional external donation charge to create.
            address:
                Optional address to create.
                We will attempt to geocode the address if ``latitude`` and ``longitude`` are not provided.
            assessment:
                Assessment status key to set on the user (maps to classification).
            sms_permission:
                SMS permission status.
            call_permission:
                Call permission status.
            email_permission:
                Email permission status.
            timezone:
                IANA timezone identifier (e.g., "America/New_York", "Europe/London").
            require_contact_info:
                Whether to require phone_number or email for user creation.
                Defaults to True.
            phone_number_textable_validation:
                Whether to validate that phone number is textable.
                Defaults to True.
            lookup_key:
                Custom property key (internal_name) to use for user lookup/deduplication.
                Value is read from ``custom_user_properties[lookup_key]``.
                Allows matching existing users by external IDs stored in custom properties.

        Raises:
            :class:`ValueError`: If neither ``phone_number`` nor ``email`` is provided.
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_users>`__

        """
        if not phone_number and not email:
            raise ValueError("Either phone_number or email must be provided")

        if isinstance(timezone, ZoneInfo):
            timezone = str(timezone.key)

        payload = {
            "phone_number": phone_number,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "alternate_name": alternate_name,
            "preferred_language": preferred_language,
            "second_language": second_language,
            "chapter_id": chapter_id,
            "chapter_ids": chapter_ids,
            "referred_by_user_id": referred_by_user_id,
            "custom_user_properties": custom_user_properties,
            "append_custom_user_properties": append_custom_user_properties,
            "add_tags": add_tags,
            "remove_tags": remove_tags,
            "donation_charge": donation_charge,
            "address": address,
            "assessment": assessment,
            "sms_permission": sms_permission,
            "call_permission": call_permission,
            "email_permission": email_permission,
            "timezone": timezone,
            "require_contact_info": require_contact_info,
            "phone_number_textable_validation": phone_number_textable_validation,
            "lookup_key": lookup_key,
        }
        res = self._post_request(
            "users", payload=payload, additional_headers={"content-type": "application/json"}
        )

        expected_responses = {
            200: (True, "user updated via lookup_key - existing user found"),
            201: (True, "user created with lookup_key - new user"),
            403: (False, "multi-chapter feature not enabled"),
            422: (False, "provided lookup_key without value in custom_user_properties"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def update_user(
        self,
        id: int,
        phone_number: str | None = None,
        clear_phone_number: bool | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        alternate_name: str | None = None,
        preferred_language: str | None = None,
        chapter_id: int | None = None,
        chapter_ids: list[int] | None = None,
        add_chapter_ids: list[int] | None = None,
        remove_chapter_ids: list[int] | None = None,
        set_exclusive_chapter: bool | None = None,
        second_language: str | None = None,
        referred_by_user_id: int | None = None,
        custom_user_properties: dict[str, str | list[str]] | None = None,
        append_custom_user_properties: bool = True,
        address: dict[str, str | float] | None = None,
        assessment: str | None = None,
        sms_permission: bool | None = None,
        call_permission: bool | None = None,
        email_permission: bool | None = None,
        timezone: ZoneInfo | str | None = None,
        donation_charge: dict[str, numbers.Number | str] | None = None,
    ) -> bool:
        """
        Update a user with the specified details.

        Args:
            id:
                Identifier of the user to update.
            phone_number:
                Phone number of the user.
            clear_phone_number:
                If True, clears the user's primary phone number
                (and removes it from ``other_phone_numbers``).
                Blank ``phone_number`` values are always ignored, so this
                explicit flag is the only way to clear a phone number via the API.
                Cannot be combined with a non-blank ``phone_number``
                in the same request (returns 422).
            email:
                Email of the user.
            first_name:
                First name of the user.
            last_name:
                Last name of the user.
            alternate_name:
                Alternate name (nickname, community name, or alternate romanization). Searchable.
                Blank values are ignored; an existing alternate name cannot be cleared via the API.
            preferred_language:
                Preferred language of the user.
            chapter_id:
                Primary chapter ID (backwards compatible).
            chapter_ids:
                Full array of chapter IDs (replaces all). Requires multi-chapter feature.
            add_chapter_ids:
                Array of chapter IDs to add. Requires multi-chapter feature.
            remove_chapter_ids:
                Array of chapter IDs to remove. Requires multi-chapter feature.
            set_exclusive_chapter:
                When True with ``chapter_id``,
                sets that chapter as the only chapter
                (removes all other chapter memberships).
            second_language:
                Second language of the user.
            referred_by_user_id:
                Identifier of the user who referred this user.
                Custom property values keyed by ``internal_name``.
                Use a string for single-value fields
                (text, number, radio, dropdown, single checkbox).
                Use an array of strings for Multiple Checkboxes fields
                (e.g. ``["Option A", "Option B"]``).
                Comma-separated strings are also accepted for Multiple Checkboxes
                (e.g. ``"Option A, Option B"``).
                For Multiple Checkboxes, see ``append_custom_user_properties`` to
                control whether values are merged with or replace existing values.
            append_custom_user_properties:
                Controls how Multiple Checkboxes custom properties are written.
                Defaults to True (union new values with existing values, the long-standing API behavior).
                Set to False to overwrite existing values, mirroring bulk update REPLACE mode.
                Has no effect on non-array field types.
            address:
                Optional address to update.
                We will attempt to geocode the address if
                latitude and longitude are not provided.
            assessment:
                Assessment status key to set on the user (maps to classification).
            sms_permission:
                If True, the user has permission to receive SMS messages.
            call_permission:
                If True, the user has permission to receive call messages.
            email_permission:
                If True, the user has permission to receive email messages.
            timezone:
                IANA timezone identifier (e.g., "America/New_York", "Europe/London").
            donation_charge:
                Optional external donation charge to create.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_users-id>`__

        """
        if isinstance(timezone, ZoneInfo):
            timezone = str(timezone.key)

        payload = {
            "phone_number": phone_number,
            "clear_phone_number": clear_phone_number,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "alternate_name": alternate_name,
            "preferred_language": preferred_language,
            "chapter_id": chapter_id,
            "chapter_ids": chapter_ids,
            "add_chapter_ids": add_chapter_ids,
            "remove_chapter_ids": remove_chapter_ids,
            "set_exclusive_chapter": set_exclusive_chapter,
            "second_language": second_language,
            "referred_by_user_id": referred_by_user_id,
            "custom_user_properties": custom_user_properties,
            "append_custom_user_properties": append_custom_user_properties,
            "address": address,
            "assessment": assessment,
            "sms_permission": sms_permission,
            "call_permission": call_permission,
            "email_permission": email_permission,
            "timezone": timezone,
            "donation_charge": donation_charge,
        }
        res = self._put_request(
            "users",
            id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            200: (True, "user updated"),
            422: (False, "cannot set and clear the phone number in the same request"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def merge_duplicate_users(
        self,
        primary_user_id: int,
        user_ids: list[int] | str,
    ) -> UserMergeMetadata:
        """
        Merge two or more users.

        Args:
            primary_user_id:
                ID of the user to keep (the survivor).
                All data from duplicates will be merged into this user.
            user_ids:
                IDs of the duplicate users to merge into the primary user.
                These users will be deactivated after merge.
                Also accepts a comma-separated string.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Data about the merge attempt.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_users-merge>`__

        """
        if isinstance(user_ids, list):
            user_ids = ",".join(str(id) for id in user_ids)

        payload = {
            "primary_user_id": primary_user_id,
            "user_ids": user_ids,
        }
        res = self._post_request(
            "users/merge",
            payload=payload,
            additional_headers={"accept": "application/json", "content-type": "application/json"},
        )

        expected_responses = {
            200: (True, "users merged successfully"),
            404: (False, "user not found"),
            422: (False, "invalid parameters"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def delete_user(
        self,
        id: str,
    ) -> UserDeleteMetadata:
        """
        Delete a user with the specified ID.

        Args:
            id:
                Identifier of the user to delete

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Data about the delete operation.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_users-id>`__

        """
        res = self._del_request("users", id, additional_headers={"accept": "application/json"})

        expected_responses = {
            200: (True, "user deleted"),
            404: (False, "user not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()
