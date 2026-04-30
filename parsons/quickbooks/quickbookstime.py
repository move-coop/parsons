import logging
from datetime import date, datetime
from typing import Literal

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons.utilities.datetime import convert_date_to_iso

# Set up logger
logger = logging.getLogger(__name__)

QB_URI = "https://rest.tsheets.com/api/v1/"


class QuickBooksTime:
    """
    Instantiate the QuickBooksTime class.

    Reference Documentation:
        `QuickBooksTime API Documentation <https://tsheetsteam.github.io/api_docs/#introduction>`__

    Args:
        token:
            A valid QuickBooksTime Auth Token.
            Not required if ``QB_AUTH_TOKEN`` env variable set.

            Learn how to obtain a token
            `here <https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0>`__

    """

    def __init__(self, token: str | None = None) -> None:
        self.token: str = check_env.check("QB_AUTH_TOKEN", token)
        self.headers = {"Authorization": "Bearer " + self.token}
        self.client = APIConnector(QB_URI, headers=self.headers)

    # Helper functions

    def qb_get_request(
        self, end_point: str, querystring: dict[str, str | int | list[str | int]] | None = None
    ) -> Table:
        """This function handles the pagination of the request"""

        # If no querystring is provided, initialize it as an empty dictionary
        if querystring is None:
            querystring = {}

        output_list = []  # This list will hold the results

        # Handle page parameter
        page: int = querystring.get("page", 1)

        more = True  # This flag indicates if there are more pages to fetch
        while more:
            # After every 10 pages, log the progress
            if page % 10 == 0:
                logger.info(f"Retrieved {len(output_list)} records from {end_point} endpoint.")
                logger.info(f"Currently on page {page}.")

            # Add the current page to the querystring
            querystring = {**querystring, **{"page": page}}

            # Send the GET request
            response = self.client.get_request(end_point, params=querystring)

            # Extract the key of the results
            endpoint_key = list(response["results"].keys())[0]

            # Extract the records from the results
            temp_list = list(response["results"][endpoint_key].values())

            # If the response indicates there are more pages,
            # update the flag and increment the page number
            more = response.get("more", False)
            page += 1

            # Add the records from the current page to the output list
            output_list.extend(temp_list)

        # Log the total number of records retrieved
        logger.info(f"Retrieved {len(output_list)} records from {end_point} endpoint.")

        # Return the results as a Table
        return Table(output_list)

    def get_groups(
        self,
        ids: list[int | str] | None = None,
        active: Literal["yes", "no", "both"] = "yes",
        manager_ids: list[int | str] | None = None,
        name: str | None = None,
        modified_before: datetime | str | None = None,
        modified_since: datetime | str | None = None,
        supplemental_data: Literal["yes", "no"] = "yes",
        limit: int = 200,
        page: int = 1,
    ) -> Table:
        """
        This function allows you to call the
        ``/groups`` endpoint of the QuickBooksTime Time API.

        Args:
            ids:
                Comma separated list of one or more group ids you'd like to filter on.
            active:
                ``yes``, ``no``, or ``both``.
                Default is ``yes``.
            manager_ids:
                Comma separated list of one or more manager ids you'd like to filter on.
            name:
                Comma separated list of one or more group names you'd like to filter on.
            modified_before:
                Only groups modified before this date/time will be returned.
                In ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            modified_since:
                Only groups modified since this date/time will be returned.
                In ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            supplemental_data:
                Indicates whether supplemental data should be returned.
                May be ``yes`` or ``no``.
                Default is ``yes``.
            limit:
                Represents how many results you'd like to retrieve per request (page).
                Default is 200.
                Max is 200.
            page: Represents the page of results you'd like to retrieve.

        """
        querystring = {
            "ids": ids,
            "active": active,
            "manager_ids": manager_ids,
            "name": name,
            "modified_before": convert_date_to_iso(modified_before),
            "modified_since": convert_date_to_iso(modified_since),
            "supplemental_data": supplemental_data,
            "limit": limit,
            "page": page,
        }

        logger.info("Retrieving groups.")
        tbl = self.qb_get_request(end_point="groups", querystring=querystring)

        logger.info(f"Found {tbl.num_rows} groups.")
        return tbl if tbl.num_rows > 0 else Table()

    def get_jobcodes(
        self,
        ids: list[int | str] | None = None,
        parent_ids: list[int | str] | None = None,
        name: str | None = None,
        type: Literal["regular", "pto", "paid_break", "unpaid_break", "all"] | None = None,
        active: Literal["yes", "no", "both"] | None = None,
        customfields: bool | None = None,
        modified_before: datetime | str | None = None,
        modified_since: datetime | str | None = None,
        supplemental_data: Literal["yes", "no"] = "yes",
        limit: int = 200,
        page: int = 1,
    ) -> Table:
        """
        This function allows you to call the
        ``/jobcodes`` endpoint of the QuickBooksTime Time API.

        Args:
            ids:
                Comma separated list of one or more jobcode ids you'd like to filter on.
                Only jobcodes with an id set to one of these values will be returned.
                If omitted, all jobcodes matching other specified filters are returned.
            parent_ids:
                Default is -1 (meaning all jobcodes will be returned regardless of parent_id).
                Comma separated list of one or more jobcode parent_ids you'd like to filter on.
                Only jobcodes with a parent_id set to one of these values will be returned.
                Additionally you can use 0 to get only the top-level jobcodes.

                Then get the id of any results with has_children=yes
                and feed that in as the value of parent_ids
                for your next request to get the 2nd level of jobcodes,
                and so on, to traverse an entire tree of jobcodes.
                Use -1 to return all jobcodes regardless of parent_id.
                This is especially useful when combined with the modified_since filter.
                When parent_ids is -1, you'll have the jobcode records needed to trace each result
                back to it's top level parent in the supplemental_data section of the response.
            name:
                ``*`` will be interpreted as a wild card.
                Starts matching from the beginning of the string.
            type:
                Indicates jobcode type.
                One of ``regular``, ``pto``, ``paid_break``, ``unpaid_break``, or ``all``.
                Default is ``regular``.
            active:
                If a jobcode is active, it is available for selection during time entry.
                May be ``yes``, ``no``, or ``both``.
                Default is ``yes``.
            customfields:
                ``True`` or ``False``.
                If ``True``, custom fields for this jobcode will be returned.
                If ``False``, the customfields object will be omitted.
            modified_before:
                Only jobcodes modified before this date/time will be returned.
                In ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            modified_since:
                Only jobcodes modified since this date/time will be returned.
                In ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            supplemental_data:
                Indicates whether supplemental data should be returned.
                May be ``yes`` or ``no``.
                Default is ``yes``.
            limit:
                Represents how many results you'd like to retrieve per request (page).
                Default is 200.
                Max is 200.
            page:
                Represents the page of results you'd like to retrieve.
                Default is 1.

        """
        querystring = {
            "ids": ids,
            "parent_ids": parent_ids,
            "name": name,
            "customfields": customfields,
            "active": active,
            "type": type,
            "modified_before": convert_date_to_iso(modified_before),
            "modified_since": convert_date_to_iso(modified_since),
            "supplemental_data": supplemental_data,
            "limit": limit,
            "page": page,
        }

        logger.info("Retrieving jobcodes.")
        tbl = self.qb_get_request(end_point="jobcodes", querystring=querystring)

        logger.info(f"Found {tbl.num_rows} jobs.")
        return tbl if tbl.num_rows > 0 else Table()

    def get_timesheets(
        self,
        ids: list[int | str] | None = None,
        jobcode_ids: list[int | str] | None = None,
        payroll_ids: list[int | str] | None = None,
        user_ids: list[int | str] | None = None,
        group_ids: list[int | str] | None = None,
        end_date: date | str | None = None,
        on_the_clock: Literal["yes", "no", "both"] = "no",
        jobcode_type: Literal["regular", "pto", "paid_break", "unpaid_break", "all"] = "all",
        modified_before: datetime | str | None = None,
        modified_since: datetime | str | None = None,
        supplemental_data: Literal["yes", "no"] = "yes",
        limit: int = 200,
        page: int = 1,
        start_date: date | str | None = "1900-01-01",
    ) -> Table:
        """
        This function allows you to call the
        ``/timesheets`` endpoint of the QuickBooksTime Time API.

        Params:
            ids:
                required (unless modified_before, modified_since, or start_date are set)
                Comma separated list of one or more timesheet ids you'd like to filter on.
                Only timesheets with an id set to one of these values will be returned.
                If omitted, all timesheets matching other specified filters are returned.
            start_date:
                required (unless modified_before, modified_since, or ids is set)
                ``YYYY-MM-DD`` formatted date.
                Any timesheets with a date falling on or after this date will be returned.
            end_date:
                ``YYYY-MM-DD`` formatted date.
                Any timesheets with a date falling on or before this date will be returned.
            jobcode_ids:
                A comma-separated string of jobcode ids.
                Only time recorded against these jobcodes or one of their children will be returned.
            payroll_ids:
                A comma-separated string of payroll ids.
                Only time recorded against users with these payroll ids will be returned.
            user_ids:
                A comma-separated list of user ids.
                Only timesheets linked to these users will be returned.
            group_ids:
                A comma-separated list of group ids.
                Only timesheets linked to users from these groups will be returned.
            on_the_clock:
                If a timesheet is on_the_clock, it means the user is currently working
                (has not clocked out yet).
                May be ``yes``, ``no``, or ``both``.
                Default is ``no``.
            jobcode_type:
                Only timesheets linked to a jobcode of the given type are returned.
                May be ``regular``, ``pto``, ``paid_break``, ``unpaid_break``, or ``all``.
                Default is ``all``.
            modified_before:
                required (unless `modified_since`, `ids`, or `start_date` are set)
                Only timesheets modified before this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).
            modified_since:
                required (unless modified_before, ids, or start_date are set)
                Only timesheets modified since this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).
            supplemental_data:
                Indicates whether supplemental data should be returned.
                May be ``yes`` or ``no``.
                Default is ``yes``.
            limit:
                Represents how many results you'd like to retrieve per request (page).
                Default is 200.
                Max is 200.
            page:
                Represents the page of results you'd like to retrieve.
                Default is 1.

        """
        querystring = {
            "ids": ids,
            "jobcode_ids": jobcode_ids,
            "payroll_ids": payroll_ids,
            "user_ids": user_ids,
            "group_ids": group_ids,
            "end_date": convert_date_to_iso(end_date),
            "on_the_clock": on_the_clock,
            "jobcode_type": jobcode_type,
            "modified_before": convert_date_to_iso(modified_before),
            "modified_since": convert_date_to_iso(modified_since),
            "supplemental_data": supplemental_data,
            "limit": limit,
            "start_date": convert_date_to_iso(start_date),
            "page": page,
        }

        logger.info("Retrieving timesheets.")
        tbl = self.qb_get_request(end_point="timesheets", querystring=querystring)

        logger.info(f"Found {tbl.num_rows} timesheets.")
        return tbl if tbl.num_rows > 0 else Table()

    def get_users(
        self,
        ids: list[int | str] | None = None,
        not_ids: list[int | str] | None = None,
        employee_numbers: list[int] | None = None,
        usernames: list[int] | None = None,
        group_ids: list[int | str] | None = None,
        not_group_ids: list[int | str] | None = None,
        payroll_ids: list[int | str] | None = None,
        active: Literal["yes", "no", "both"] = "yes",
        first_name: str | None = None,
        last_name: str | None = None,
        modified_before: datetime | str | None = None,
        modified_since: datetime | str | None = None,
        supplemental_data: Literal["yes", "no"] = "yes",
        limit: int = 200,
        page: int = 1,
    ) -> Table:
        """
        This function allows you to call the
        ``/users`` endpoint of the QuickBooksTime Time API.

        Args:
            ids:
                Comma separated list of one or more user ids you'd like to filter on.
            not_ids:
                Comma separated list of one or more user ids you'd like to filter on.
                Specifically, the user ids you'd like to exclude.
            employee_numbers:
                Comma separated list of one or more employee numbers you'd like to filter on.
            usernames:
                Comma separated list of one or more usernames you'd like to filter on.
            group_ids:
                Comma separated list of one or more group ids you'd like to filter on.
            not_group_ids:
                Comma separated list of one or more group ids you'd like to filter on.
                Specifically, the group ids you'd like to exclude.
            payroll_ids:
                A comma-separated string of payroll ids.
                Only users with these payroll ids will be returned.
            active:
                May be ``yes``, ``no``, or ``both``.
                Default is ``yes``.
            first_name:
                ``*`` will be interpreted as a wild card.
                Starts matching from the beginning of the string.
            last_name:
                ``*`` will be interpreted as a wild card.
                Starts matching from the beginning of the string.
            modified_before:
                Only users modified before this date/time will be returned.
                In ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            modified_since:
                Only users modified since this date/time will be returned.
                In ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            supplemental_data:
                Indicates whether supplemental data should be returned.
                May be ``yes`` or ``no``.
                Default is ``yes``.
            limit:
                Represents how many results you'd like to retrieve per request (page).
                Default is 200.
                Max is 200.
            page:
                Represents the page of results you'd like to retrieve.
                Default is 1.

        """
        querystring = {
            "ids": ids,
            "not_ids": not_ids,
            "employee_numbers": employee_numbers,
            "usernames": usernames,
            "group_ids": group_ids,
            "not_group_ids": not_group_ids,
            "payroll_ids": payroll_ids,
            "active": active,
            "first_name": first_name,
            "last_name": last_name,
            "modified_before": convert_date_to_iso(modified_before),
            "modified_since": convert_date_to_iso(modified_since),
            "supplemental_data": supplemental_data,
            "limit": limit,
            "page": page,
        }

        logger.info("Retrieving users.")
        tbl = self.qb_get_request(end_point="users", querystring=querystring)

        logger.info(f"Found {tbl.num_rows} users.")
        return tbl if tbl.num_rows > 0 else Table()

    def get_schedule_calendars_list(
        self,
        ids: list[int | str] | None = None,
        modified_before: datetime | str | None = None,
        modified_since: datetime | str | None = None,
        supplemental_data: Literal["yes", "no"] = "yes",
        limit: int = 200,
        page: int = 1,
    ) -> list[int]:
        """
        This function allows you to call the
        ``/schedule_calendars`` endpoint of the QuickBooksTime Time API.

        Args:
            ids:
                Comma separated list of one or more schedule calendar ids you'd like to filter on.
                Only schedule calendars with an id set to one of these values will be returned.
            modified_before:
                Only schedule calendars modified before this date/time will be returned,
                in ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            modified_since:
                required (unless `ids`, `modified_before`, or ``start`` are set)
                Only schedule calendars modified since this date/time will be returned,
                in ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            supplemental_data:
                ``yes`` or ``no``.
                Default is ``yes``.
                Indicates whether supplemental data should be returned.
            limit:
                Represents how many results you'd like to retrieve per request (page).
                Default is 200.
                Max is 200.
            page:
                Represents the page of results you'd like to retrieve.
                Default is 1.

        Returns:
            List of integers of schedules calendar ids.
            Needed for calling the ``/schedule_events`` endpoint

        """
        endpoint = "schedule_calendars"

        querystring = {
            "ids": ids,
            "modified_before": convert_date_to_iso(modified_before),
            "modified_since": convert_date_to_iso(modified_since),
            "supplemental_data": supplemental_data,
            "limit": limit,
            "page": page,
        }

        logger.info("Retrieving schedule calendars.")
        tbl = self.qb_get_request(end_point=endpoint, querystring=querystring)

        schedule_calendar_ids_list = [
            int(row["id"]) for row in tbl
        ]  # Creates list of integers of the schedule_calendar_ids

        logger.info(f"Found {tbl.num_rows} schedule calendars.")
        return schedule_calendar_ids_list

    def get_schedule_events(
        self,
        ids: list[int | str] | None = None,
        users_ids: list[int | str] | None = None,
        schedule_calendar_ids: list[int | str] | None = None,
        jobcode_ids: list[int | str] | None = None,
        start: datetime | str = "1970-01-01T00:00:00+00:00",
        end: datetime | str | None = None,
        active_users: Literal[0, -1, 1] = 1,
        active: Literal["yes", "no", "both"] = "both",
        draft: Literal["yes", "no", "both"] = "no",
        team_events: Literal["base", "instance"] = "instance",
        modified_before: datetime | str | None = None,
        modified_since: datetime | str | None = None,
        supplemental_data: Literal["yes", "no"] = "yes",
        limit: int = 200,
        page: int = 1,
    ) -> Table:
        """
        This function allows you to call the /schedule_events endpoint
        of the QuickBooksTime Time API.

        Args:
            ids:
                required (unless `modified_before`, `modified_since`, or `start` are set)
                Comma separated list of one or more schedule event ids you'd like to filter on.
                Only schedule events with an id set to one of these values will be returned.
            users_ids:
                Comma-separated list of one or more user ids to retrieve schedule events for.
            schedule_calendar_ids:
                Comma separated list of one or more schedule calendar ids you'd like to filter on.
                Only schedule events with a schedule calendar id
                set to one of these values will be returned.
            jobcode_ids:
                A comma-separated string of jobcode ids.
                Only schedule events with these jobcodes will be returned.
            start:
                required (unless `ids`, `modified_before`, or `modified_since` are set)
                Only schedule events starting on or after this date/time will be returned,
                in ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            end:
                Only schedule events ending on or before this date/time will be returned,
                in ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            active:
                Only ``schedule events`` whose active state match the requested filter will be returned.
                ``yes``, ``no`` or ``both``.
                Default is ``both``.
            active_users:
                Get ``schedule events`` for users based on activity status.
                ``1`` will return events for active users.
                ``0`` will return events for inactive users.
                ``-1`` will return events for active and inactive users.
                Default is ``1``.
            draft:
                Only ``schedule events`` whose draft state match the requested filter will be returned.
                ``yes``, ``no`` or ``both``.
                Default is ``no``.
            team_events:
                If ``instance`` is specified, events that are assigned to multiple users
                will be returned as individual single events for each assigned user.
                If 'base' is specified, events that are assigned to multiple users
                will be returned as one combined event for all assignees.
                Default is ``instance``.
            modified_before:
                required (unless `ids`, `modified_since`, or `start` are set)
                Only schedule events modified before this date/time will be returned,
                in ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            modified_since:
                required (unless `ids`, `modified_before`, or `start` are set)
                Only schedule events modified since this date/time will be returned,
                in ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
            supplemental_data:
                Indicates whether supplemental data should be returned.
                ``yes`` or ``no``.
                Default is ``yes``.
            limit:
                Represents how many results you'd like to retrieve per request (page).
                Default is 200.
                Max is 200.
            page:
                Represents the page of results you'd like to retrieve.
                Default is 1.

        """
        if schedule_calendar_ids is None:
            schedule_calendar_ids = self.get_schedule_calendars_list()

        endpoint = "schedule_events"

        querystring = {
            "ids": ids,
            "users_ids": users_ids,
            "schedule_calendar_ids": schedule_calendar_ids,
            "jobcode_ids": jobcode_ids,
            "start": convert_date_to_iso(start),
            "end": convert_date_to_iso(end),
            "active": active,
            "active_users": active_users,
            "draft": draft,
            "team_events": team_events,
            "modified_before": convert_date_to_iso(modified_before),
            "modified_since": convert_date_to_iso(modified_since),
            "supplemental_data": supplemental_data,
            "limit": limit,
            "page": page,
        }

        logger.info("Retrieving schedule events.")
        tbl = self.qb_get_request(end_point=endpoint, querystring=querystring)

        logger.info(f"Found {tbl.num_rows} schedules.")
        return tbl if tbl.num_rows > 0 else Table()

    def get_geolocations(
        self,
        ids: list[int | str] | None = None,
        modified_before: datetime | str | None = None,
        modified_since: datetime | str | None = None,
        user_ids: list[int | str] | None = None,
        group_ids: list[int | str] | None = None,
        supplemental_data: Literal["yes", "no"] = "yes",
        limit: int = 200,
        page: int = 1,
    ) -> Table:
        """
        This function allows you to call the /geolocations endpoint of the QuickBooksTime Time API.

        Args:
            ids:
                Comma separated list of one or more geolocation ids you'd like to filter on.
                Only geolocations with an id set to one of these values will be returned.
                Required (unless modified_before, modified_since is set)
            modified_before:
                Only geolocations modified before this date/time will be returned,
                in ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
                Required (unless ids or modified_since is set)
            modified_since:
                Only geolocations modified since this date/time will be returned,
                in ISO 8601 format (``YYYY-MM-DDThh:mm:ss±hh:mm``).
                Required (unless ids or modified_before is set)
            user_ids:
                Comma separated list of one or more user ids you'd like to filter on.
                Only geolocations with a user id set to one of these values will be returned.
            group_ids:
                Comma separated list of one or more group ids you'd like to filter on.
                Only geolocations with a group id set to one of these values will be returned.
            suplemental_data:
                Indicates whether supplemental data should be returned.
                ``yes`` or ``no``.
                Default is ``yes``.
            limit:
                Represents how many results you'd like to retrieve per request (page).
                Default is 200.
                Max is 200.
            page:
                Represents the page of results you'd like to retrieve.
                Default is 1.

        """
        endpoint = "geolocations"

        querystring = {
            "ids": ids,
            "modified_before": convert_date_to_iso(modified_before),
            "modified_since": convert_date_to_iso(modified_since),
            "user_ids": user_ids,
            "group_ids": group_ids,
            "supplemental_data": supplemental_data,
            "limit": limit,
            "page": page,
        }

        logger.info("Retrieving geolocations.")
        tbl = self.qb_get_request(end_point=endpoint, querystring=querystring)

        logger.info(f"Found {tbl.num_rows} geolocations.")
        return tbl if tbl.num_rows > 0 else Table()
