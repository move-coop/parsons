import logging
from typing import Literal

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

# Set up logger
logger = logging.getLogger(__name__)

QB_URI = "https://rest.tsheets.com/api/v1/"


class QuickBooksTime:
    """
    Instantiate the QuickBooksTime class.

    Args:
        token (str, optional): A valid QuickBooksTime Auth Token. Not required if ``QB_AUTH_TOKEN`` env variable
            set.
            [Find instructions to create yours
            here](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)
            # noqa: E501

            [QuickBooksTime API Documentation](https://tsheetsteam.github.io/api_docs/#introduction).
            Defaults to None.

    """

    def __init__(self, token=None):
        self.token = check_env.check("QB_AUTH_TOKEN", token)
        self.headers = {"Authorization": "Bearer " + self.token}
        self.client = APIConnector(QB_URI, headers=self.headers)

    # Helper functions

    def qb_get_request(self, end_point: str, querystring=None):
        """Handles the pagination of the quickbooks request."""
        # If no querystring is provided, initialize it as an empty dictionary
        if querystring is None:
            querystring = {}

        output_list = []  # This list will hold the results

        # Handle page parameter
        page = querystring.get("page", 1)

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
        ids=None,
        active: Literal["yes", "no", "both"] = None,
        manager_ids=None,
        name=None,
        modified_before=None,
        modified_since=None,
        supplemental_data: Literal["yes", "no"] = None,
        limit=None,
        page=1,
    ):
        """
        Call the /groups endpoint of the QuickBooksTime Time API.

        All arguments are optional.

        Args:
            ids (int, optional): Comma separated list of one or more group ids you'd like to filter on.
                Defaults to None.
            active (Literal["yes", "no", "both"], optional): Defaults to None.
            manager_ids (int, optional): Comma separated list of one or more manager ids you'd like to filter on.
                Defaults to None.
            name (str, optional): Comma separated list of one or more group names you'd like to filter on.
                Defaults to None.
            modified_before (str, optional): Only groups modified before this date/time will be returned, in ISO
                8601 format (YYYY-MM-DDThh:mm:ss±hh:mm). Defaults to None.
            modified_since (str, optional): Only groups modified since this date/time will be returned, in ISO 8601
                format (YYYY-MM-DDThh:mm:ss±hh:mm). Defaults to None.
            supplemental_data (Literal["yes", "no"], optional): Indicates whether supplemental data should be
                returned. Defaults to None.
            limit (int, optional): Represents how many results you'd like to retrieve per request (page).
                Max is. Defaults to None.
            page (int, optional): Represents the page of results you'd like to retrieve. Defaults to 1.

        Returns:
            Parsons Table

        """
        querystring = {
            "ids": ids,
            "active": active,
            "manager_ids": manager_ids,
            "name": name,
            "modified_before": modified_before,
            "modified_since": modified_since,
            "supplemental_data": supplemental_data,
            "limit": limit,
            "page": page,
        }

        logger.info("Retrieving groups.")
        tbl = self.qb_get_request(end_point="groups", querystring=querystring)

        logger.info(f"Found {tbl.num_rows} groups.")
        if tbl.num_rows > 0:
            return tbl
        else:
            return Table()

    def get_jobcodes(
        self,
        ids=None,
        parent_ids=None,
        name=None,
        type=None,
        active: Literal["yes", "no", "both"] = None,
        customfields=None,
        modified_before=None,
        modified_since=None,
        supplemental_data: Literal["yes", "no"] = None,
        limit=None,
        page=1,
    ):
        """
        Call the /jobcodes endpoint of the QuickBooksTime Time API.

        Args:
            ids (int, optional): Comma separated list of one or more jobcode ids you'd like to filter on.
                Only jobcodes with an id set to one of these values will be returned. If omitted, all jobcodes matching
                other specified filters are returned. Defaults to None.
            parent_ids: Int Comma separated list of one or more jobcode parent_ids you'd like to filter on.
                Only jobcodes with a parent_id set to one of these values will be returned. Additionally you can use 0
                to get only the top-level jobcodes.

                Then get the id of any results with has_children=yes and feed that in as the value of parent_ids for
                your next request to get the 2nd level of jobcodes, and so on, to traverse an entire tree of jobcodes.
                Use -1 to return all jobcodes regardless of parent_id. This is especially useful when combined with the
                modified_since filter. When parent_ids is -1, you'll have the jobcode records needed to trace each
                result back to it's top level parent in the supplemental_data section of the response.
                Defaults to None.
            name: String
                * will be interpreted as a wild card. Starts matching from the beginning of the string.
                Defaults to None.
            type (str, optional): Indicates jobcode type. One of 'regular', 'pto', 'paid_break',
                'unpaid_break', or 'all'. Defaults to None.
            active (Literal["yes", "no", "both"], optional): If a jobcode is active, it is available for selection
                during time entry. Defaults to None.
            customfields (bool, optional): If true, custom fields for this jobcode will be returned.
                If false, the customfields object will be omitted. Defaults to None.
            modified_before (str, optional): Only jobcodes modified before this date/time will be returned, in ISO
                8601 format (YYYY-MM-DDThh:mm:ss±hh:mm). Defaults to None.
            modified_since (str, optional): Only jobcodes modified since this date/time will be returned, in ISO
                8601 format (YYYY-MM-DDThh:mm:ss±hh:mm). Defaults to None.
            supplemental_data (Literal["yes", "no"], optional): Indicates whether supplemental data should be
                returned. Defaults to None.
            limit (int, optional): Represents how many results you'd like to retrieve per request (page).
                Max is. Defaults to None.
            page (int, optional): Represents the page of results you'd like to retrieve. Defaults to 1.

        Returns:
            Parsons Table

        """
        querystring = {
            "ids": ids,
            "parent_ids": parent_ids,
            "name": name,
            "customfields": customfields,
            "active": active,
            "type": type,
            "modified_before": modified_before,
            "modified_since": modified_since,
            "supplemental_data": supplemental_data,
            "limit": limit,
            "page": page,
        }

        logger.info("Retrieving jobcodes.")
        tbl = self.qb_get_request(end_point="jobcodes", querystring=querystring)

        logger.info(f"Found {tbl.num_rows} jobs.")
        if tbl.num_rows > 0:
            return tbl
        else:
            return Table()

    def get_timesheets(
        self,
        ids=None,
        jobcode_ids=None,
        payroll_ids=None,
        user_ids=None,
        group_ids=None,
        end_date=None,
        on_the_clock=None,
        jobcode_type=None,
        modified_before=None,
        modified_since=None,
        supplemental_data: Literal["yes", "no"] = None,
        limit=None,
        page=1,
        start_date="1900-01-01",
    ):
        """
        Call the /timesheets endpoint of the QuickBooksTime Time API.

        Args:
            start_date: Defaults to "1900-01-01".
            page: Defaults to 1.
            limit: Defaults to None.
            supplemental_data (Literal["yes", "no"], optional): Defaults to None.
            modified_since: Defaults to None.
            modified_before: Defaults to None.
            jobcode_type: Defaults to None.
            on_the_clock: Defaults to None.
            end_date: Defaults to None.
            group_ids: Defaults to None.
            user_ids: Defaults to None.
            payroll_ids: Defaults to None.
            jobcode_ids: Defaults to None.
            ids: Defaults to None.

        Returns:
            Parsons Table

        Params:

        """
        querystring = {
            "ids": ids,
            "jobcode_ids": jobcode_ids,
            "payroll_ids": payroll_ids,
            "user_ids": user_ids,
            "group_ids": group_ids,
            "end_date": end_date,
            "on_the_clock": on_the_clock,
            "jobcode_type": jobcode_type,
            "modified_before": modified_before,
            "modified_since": modified_since,
            "supplemental_data": supplemental_data,
            "limit": limit,
            "start_date": start_date,
            "page": page,
        }

        logger.info("Retrieving timesheets.")
        tbl = self.qb_get_request(end_point="timesheets", querystring=querystring)

        logger.info(f"Found {tbl.num_rows} timesheets.")
        if tbl.num_rows > 0:
            return tbl
        else:
            return Table()

    def get_users(
        self,
        ids=None,
        not_ids=None,
        employee_numbers=None,
        usernames=None,
        group_ids=None,
        not_group_ids=None,
        payroll_ids=None,
        active: Literal["yes", "no", "both"] = None,
        first_name=None,
        last_name=None,
        modified_before=None,
        modified_since=None,
        supplemental_data: Literal["yes", "no"] = None,
        limit=None,
        page=1,
    ):
        """
        Call the /users endpoint of the QuickBooksTime Time API.

        Args:
            ids (int, optional): Comma separated list of one or more user ids you'd like to filter on.
                Defaults to None.
            not_ids (int, optional): Comma separated list of one or more user ids you'd like to filter on.
                Specifically, the user ids you'd like to exclude. Defaults to None.
            employee_numbers (int, optional): Comma separated list of one or more employee numbers you'd like to
                filter on. Defaults to None.
            usernames (str, optional): Comma separated list of one or more usernames you'd like to filter on.
                Defaults to None.
            group_ids (int, optional): Comma separated list of one or more group ids you'd like to filter on.
                Defaults to None.
            not_group_ids (int, optional): Comma separated list of one or more group ids you'd like to filter on.
                Specifically, the group ids you'd like to exclude. Defaults to None.
            payroll_ids (str, optional): A comma-separated string of payroll ids. Only users with these payroll ids
                will be returned. Defaults to None.
            active (Literal["yes", "no", "both"], optional): Defaults to None.
            first_name: String
                * will be interpreted as a wild card. Starts matching from the beginning of the string.
                Defaults to None.
            last_name: String
                * will be interpreted as a wild card. Starts matching from the beginning of the string.
                Defaults to None.
            modified_before (str, optional): Only users modified before this date/time will be returned, in ISO 8601
                format (YYYY-MM-DDThh:mm:ss±hh:mm). Defaults to None.
            modified_since (str, optional): Only users modified since this date/time will be returned, in ISO 8601
                format (YYYY-MM-DDThh:mm:ss±hh:mm). Defaults to None.
            supplemental_data (Literal["yes", "no"], optional): Indicates whether supplemental data should be
                returned. Defaults to None.
            limit (int, optional): Represents how many results you'd like to retrieve per request (page).
                Max is. Defaults to None.
            page (int, optional): Represents the page of results you'd like to retrieve. Defaults to 1.

        Returns:
            Parsons Table
            See Parsons Table for output options.

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
            "modified_before": modified_before,
            "modified_since": modified_since,
            "supplemental_data": supplemental_data,
            "limit": limit,
            "page": page,
        }

        logger.info("Retrieving users.")
        tbl = self.qb_get_request(end_point="users", querystring=querystring)

        logger.info(f"Found {tbl.num_rows} users.")
        if tbl.num_rows > 0:
            return tbl
        else:
            return Table()

    def get_schedule_calendars_list(
        self,
        ids=None,
        modified_before=None,
        modified_since=None,
        supplemental_data: Literal["yes", "no"] = None,
        limit=None,
        page=1,
    ):
        """
        Call the /schedule_calendars endpoint of the QuickBooksTime Time API.

        Args:
            ids (int, optional): Comma separated list of one or more schedule calendar ids you'd like to filter on.
                Only schedule calendars with an id set to one of these values will be returned.
                Defaults to None.
            modified_before (str, optional): Only schedule calendars modified before this date/time will be
                returned, in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm). Defaults to None.
            modified_since (str, optional): Required (unless ids, modified_before, or start are set) Only schedule
                calendars modified since this date/time will be returned, in ISO 8601 format
                (YYYY-MM-DDThh:mm:ss±hh:mm). Defaults to None.
            supplemental_data (Literal["yes", "no"], optional): Indicates whether supplemental data should be
                returned. Defaults to None.
            limit (int, optional): Represents how many results you'd like to retrieve per request (page).
                Max is. Defaults to None.
            page (int, optional): Represents the page of results you'd like to retrieve. Defaults to 1.

        Returns:
            List of integers of schedules calendar ids.
            Needed for calling the /schedule_events endpoint

        """
        endpoint = "schedule_calendars"

        querystring = {
            "ids": ids,
            "modified_before": modified_before,
            "modified_since": modified_since,
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
        ids=None,
        users_ids=None,
        schedule_calendar_ids=None,
        jobcode_ids=None,
        start="1970-01-01T00:00:00+00:00",
        end=None,
        active_users: Literal[0, -1, 1] = None,
        active: Literal["yes", "no", "both"] = None,
        draft: Literal["yes", "no", "both"] = None,
        team_events: Literal["base", "instance"] = None,
        modified_before=None,
        modified_since=None,
        supplemental_data: Literal["yes", "no"] = None,
        limit=None,
        page=1,
    ):
        """
        Call the /schedule_events endpoint of the QuickBooksTime Time API.

        Args:
            ids (int): Required (unless modified_before, modified_since, or start are set) Comma separated list of
                one or more schedule event ids you'd like to filter on. Only schedule events with an id set to one of
                these values will be returned.
            users_ids (int): Comma-separated list of one or more user ids to retrieve schedule events for.
            schedule_calendar_ids (int): Required. Comma separated list of one or more schedule calendar ids you'd
                like to filter on. Only schedule events with a schedule calendar id set to one of these values will be
                returned.
            jobcode_ids (int): A comma-separated string of jobcode ids. Only schedule events with these jobcodes
                will be returned.
            start (str): Required (unless ids, modified_before, or modified_since are set) Only schedule events
                starting on or after this date/time will be returned, in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).
            end (str): Only schedule events ending on or before this date/time will be returned, in ISO 8601 format
                (YYYY-MM-DDThh:mm:ss±hh:mm).
            active (Literal["yes", "no", "both"], optional): Only schedule events whose active state match the
                requested filter will be returned. Defaults to 'both'.
            active_users (Literal[0,-1,1], optional): Only schedule events whose users are active will be returned
                by default.
                0 will return events for inactive users.
                -1 will return events for active and inactive users. Defaults to '1'.
            draft (Literal["yes", "no", "both"], optional): Only schedule events whose draft state match the
                requested filter will be returned. Defaults to 'no'.
            team_events (Literal["base", "instance"], optional): If 'instance' is specified, events that are
                assigned to multiple users will be returned as individual single events for each assigned user.
                If 'base' is specified, events that are assigned to multiple users will be returned as one combined
                event for all assignees. Defaults to 'instance'.
            modified_before (str): Required (unless ids, modified_since, or start are set) Only schedule events
                modified before this date/time will be returned, in ISO 8601 format
                (YYYY-MM-DDThh:mm:ss±hh:mm).
            modified_since (str): Required (unless ids, modified_before, or start are set) Only schedule events
                modified since this date/time will be returned, in ISO 8601 format
                (YYYY-MM-DDThh:mm:ss±hh:mm).
            supplemental_data (Literal["yes", "no"], optional): Indicates whether supplemental data should be
                returned. Defaults to 'yes'.
            limit (int, optional): Represents how many results you'd like to retrieve per request (page).
                Max is. Defaults to 200.
            page (int, optional): Represents the page of results you'd like to retrieve. Defaults to 1.

        Returns:
            Parsons Table
            See Parsons Table for output options.

        """
        if schedule_calendar_ids is None:
            schedule_calendar_ids = self.get_schedule_calendars_list()

        endpoint = "schedule_events"

        querystring = {
            "ids": ids,
            "users_ids": users_ids,
            "schedule_calendar_ids": schedule_calendar_ids,
            "jobcode_ids": jobcode_ids,
            "start": start,
            "end": end,
            "active": active,
            "active_users": active_users,
            "draft": draft,
            "team_events": team_events,
            "modified_before": modified_before,
            "modified_since": modified_since,
            "supplemental_data": supplemental_data,
            "limit": limit,
            "page": page,
        }

        logger.info("Retrieving schedule events.")
        tbl = self.qb_get_request(end_point=endpoint, querystring=querystring)

        logger.info(f"Found {tbl.num_rows} schedules.")
        if tbl.num_rows > 0:
            return tbl
        else:
            return Table()

    def get_geolocations(
        self,
        ids=None,
        modified_before=None,
        modified_since=None,
        user_ids=None,
        group_ids=None,
        supplemental_data: Literal["yes", "no"] = None,
        limit=None,
        page=1,
    ):
        """
        Call the /geolocations endpoint of the QuickBooksTime Time API.

        Args:
            ids (int, optional): Comma separated list of one or more geolocation ids you'd like to filter on.
                Only geolocations with an id set to one of these values will be returned. Required (unless
                modified_before, modified_since is set). Defaults to None.
            modified_before (str, optional): Only geolocations modified before this date/time will be returned, in
                ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm). Required (unless ids or modified_since is set).
                Defaults to None.
            modified_since (str, optional): Only geolocations modified since this date/time will be returned, in ISO
                8601 format (YYYY-MM-DDThh:mm:ss±hh:mm). Required (unless ids or modified_before is set).
                Defaults to None.
            user_ids (int, optional): Comma separated list of one or more user ids you'd like to filter on.
                Only geolocations with a user id set to one of these values will be returned. Defaults to None.
            group_ids (int, optional): Comma separated list of one or more group ids you'd like to filter on.
                Only geolocations with a group id set to one of these values will be returned.
                Defaults to None.
            supplemental_data (Literal["yes", "no"], optional): Indicates whether supplemental data should be
                returned. Defaults to None.
            limit (int, optional): Represents how many results you'd like to retrieve per request (page).
                Max is. Defaults to None.
            page (int, optional): Represents the page of results you'd like to retrieve. Defaults to 1.

        Returns:
            Parsons Table
            See Parsons Table for output options.

        """
        endpoint = "geolocations"

        querystring = {
            "ids": ids,
            "modified_before": modified_before,
            "modified_since": modified_since,
            "user_ids": user_ids,
            "group_ids": group_ids,
            "supplemental_data": supplemental_data,
            "limit": limit,
            "page": page,
        }

        logger.info("Retrieving geolocations.")
        tbl = self.qb_get_request(end_point=endpoint, querystring=querystring)

        logger.info(f"Found {tbl.num_rows} geolocations.")

        if tbl.num_rows > 0:
            return tbl
        else:
            return Table()
