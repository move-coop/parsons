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
        token: str
            A valid QuickBooksTime Auth Token. Not required if ``QB_AUTH_TOKEN`` env
            variable set.
            [Find instructions to create yours here](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0) # noqa: E501

            [QuickBooksTime API Documentation](https://tsheetsteam.github.io/api_docs/#introduction)

    """

    def __init__(self, token=None):
        self.token = check_env.check("QB_AUTH_TOKEN", token)
        self.headers = {"Authorization": "Bearer " + self.token}
        self.client = APIConnector(QB_URI, headers=self.headers)

    # Helper functions

    def qb_get_request(self, end_point: str, querystring=None):
        """This function handles the pagination of the request"""

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
        active=None,
        manager_ids=None,
        name=None,
        modified_before=None,
        modified_since=None,
        supplemental_data: Literal["yes", "no"] = "yes",
        limit=None,
        page=1,
    ):
        """
            This function allows you to call the /groups endpoint of the QuickBooksTime Time API.
            All Args are optional.

        Args:
                ids: Int
                    Comma separated list of one or more group ids you'd like to filter on.

                active: String
                    'yes', 'no', or 'both'. Default is 'yes'.

                manager_ids: Int
                    Comma separated list of one or more manager ids you'd like to filter on.

                name: String
                    Comma separated list of one or more group names you'd like to filter on.

                modified_before: String
                    Only groups modified before this date/time will be returned,
                    in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm)

                modified_since: String
                    Only groups modified since this date/time will be returned,
                    in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm)

                supplemental_data: String
                    'yes' or 'no'. Default is 'yes'.
                    Indicates whether supplemental data should be returned.

                limit: Int
                    Represents how many results you'd like to retrieve per request (page).
                    Default is 200. Max is 200.

                page: Int
                    Represents the page of results you'd like to retrieve.

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
        type: Literal["regular", "pto", "paid_break", "unpaid_break", "all"] | None = None,
        active: Literal["yes", "no", "both"] | None = None,
        customfields=None,
        modified_before=None,
        modified_since=None,
        supplemental_data: Literal["yes", "no"] = "yes",
        limit=None,
        page=1,
    ):
        """
        This function allows you to call the /jobcodes endpoint of the QuickBooksTime Time API.

        Args:
            ids: Int
                Comma separated list of one or more jobcode ids you'd like to filter on.
                Only jobcodes with an id set to one of these values will be returned.
                If omitted, all jobcodes matching other specified filters are returned.

            parent_ids: Int
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

            name: String
                ``*`` will be interpreted as a wild card.
                Starts matching from the beginning of the string.

            type: String
                Indicates jobcode type. One of 'regular', 'pto', 'paid_break', 'unpaid_break',
                or 'all'. Default is 'regular'.

            active: String
                'yes', 'no', or 'both'. Default is 'yes'. If a jobcode is active,
                it is available for selection during time entry.

            customfields: Boolean
                true or false. If true, custom fields for this jobcode will be returned.
                If false, the customfields object will be omitted.

            modified_before: String
                Only jobcodes modified before this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            modified_since: String
                Only jobcodes modified since this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            supplemental_data: String
                'yes' or 'no'. Default is 'yes'.
                Indicates whether supplemental data should be returned.

            limit: Int
                Represents how many results you'd like to retrieve per request (page).
                Default is 200. Max is 200.

            page: Int
                Represents the page of results you'd like to retrieve. Default is 1.

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
        supplemental_data: Literal["yes", "no"] = "yes",
        limit=None,
        page=1,
        start_date="1900-01-01",
    ):
        """
        This function allows you to call the /timesheets endpoint of the QuickBooksTime Time API.

        Params:
            ids: Int
                required (unless modified_before, modified_since, or start_date are set)
                Comma separated list of one or more timesheet ids you'd like to filter on.
                Only timesheets with an id set to one of these values will be returned.
                If omitted, all timesheets matching other specified filters are returned.

            start_date: String
                required (unless modified_before, modified_since, or ids is set)
                YYYY-MM-DD formatted date.
                Any timesheets with a date falling on or after this date will be returned.

            end_date: String
                YYYY-MM-DD formatted date.
                Any timesheets with a date falling on or before this date will be returned.

            jobcode_ids: Int
                A comma-separated string of jobcode ids.
                Only time recorded against these jobcodes or one of their children will be returned.

            payroll_ids: Int
                A comma-separated string of payroll ids.
                Only time recorded against users with these payroll ids will be returned.

            user_ids: Int
                A comma-separated list of user ids.
                Only timesheets linked to these users will be returned.

            group_ids: Int
                A comma-separated list of group ids.
                Only timesheets linked to users from these groups will be returned.

            on_the_clock: String
                'yes', 'no', or 'both'. Default is 'no'.
                If a timesheet is on_the_clock, it means the user is currently working
                (has not clocked out yet).

            jobcode_type: String
                'regular', 'pto', 'paid_break', 'unpaid_break', or 'all'. Default is 'all'.
                Only timesheets linked to a jobcode of the given type are returned.

            modified_before: String
                required (unless modified_since, ids, or start_date are set)
                Only timesheets modified before this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            modified_since: String
                required (unless modified_before, ids, or start_date are set)
                Only timesheets modified since this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            supplemental_data: String
                'yes' or 'no'. Default is 'yes'.
                Indicates whether supplemental data should be returned.

            limit: Int
                Represents how many results you'd like to retrieve per request (page).
                Default is 200. Max is 200.

            page: Int
                Represents the page of results you'd like to retrieve. Default is 1.

        Returns:
            Parsons Table

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
        active=None,
        first_name=None,
        last_name=None,
        modified_before=None,
        modified_since=None,
        supplemental_data: Literal["yes", "no"] = "yes",
        limit=None,
        page=1,
    ):
        """
        This function allows you to call the /users endpoint of the QuickBooksTime Time API.

        Args:
            ids: Int
                Comma separated list of one or more user ids you'd like to filter on.

            not_ids: Int
                Comma separated list of one or more user ids you'd like to filter on.
                Specifically, the user ids you'd like to exclude.

            employee_numbers: Int
                Comma separated list of one or more employee numbers you'd like to filter on.

            usernames: Str
                Comma separated list of one or more usernames you'd like to filter on.

            group_ids: Int
                Comma separated list of one or more group ids you'd like to filter on.

            not_group_ids: Int
                Comma separated list of one or more group ids you'd like to filter on.
                Specifically, the group ids you'd like to exclude.

            payroll_ids: String
                A comma-separated string of payroll ids.
                Only users with these payroll ids will be returned.

            active: String
                'yes', 'no', or 'both'. Default is 'yes'.

            first_name: String
                ``*`` will be interpreted as a wild card.
                Starts matching from the beginning of the string.

            last_name: String
                ``*`` will be interpreted as a wild card.
                Starts matching from the beginning of the string.

            modified_before: String
                Only users modified before this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            modified_since: String
                Only users modified since this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            supplemental_data: String
                'yes' or 'no'. Default is 'yes'.
                Indicates whether supplemental data should be returned.

            limit: Int
                Represents how many results you'd like to retrieve per request (page).
                Default is 200. Max is 200.

            page: Int
                Represents the page of results you'd like to retrieve. Default is 1.

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
        supplemental_data: Literal["yes", "no"] = "yes",
        limit=None,
        page=1,
    ):
        """
        This function allows you to call the /schedule_calendars endpoint
        of the QuickBooksTime Time API.

        Args:
            ids: Int
                Comma separated list of one or more schedule calendar ids you'd like to filter on.
                Only schedule calendars with an id set to one of these values will be returned.

            modified_before: String
                Only schedule calendars modified before this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            modified_since: String
                required (unless ids, modified_before, or start are set)
                Only schedule calendars modified since this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            supplemental_data: String
                'yes' or 'no'. Default is 'yes'.
                Indicates whether supplemental data should be returned.

            limit: Int
                Represents how many results you'd like to retrieve per request (page).
                Default is 200. Max is 200.

            page: Int
                Represents the page of results you'd like to retrieve. Default is 1.

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
        active_users: Literal[0, -1, 1] = 1,
        active=None,
        draft: Literal["yes", "no", "both"] = "no",
        team_events: Literal["base", "instance"] = "instance",
        modified_before=None,
        modified_since=None,
        supplemental_data: Literal["yes", "no"] = "yes",
        limit=None,
        page=1,
    ):
        """
        This function allows you to call the /schedule_events endpoint
        of the QuickBooksTime Time API.

        Args:
            ids: Int
                required (unless modified_before, modified_since, or start are set)
                Comma separated list of one or more schedule event ids you'd like to filter on.
                Only schedule events with an id set to one of these values will be returned.

            users_ids: Int
                Comma-separated list of one or more user ids to retrieve schedule events for.

            schedule_calendar_ids: Int
                Required.
                Comma separated list of one or more schedule calendar ids you'd like to filter on.
                Only schedule events with a schedule calendar id
                set to one of these values will be returned.

            jobcode_ids: Int
                A comma-separated string of jobcode ids.
                Only schedule events with these jobcodes will be returned.

            start: String
                required (unless ids, modified_before, or modified_since are set)
                Only schedule events starting on or after this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            end: String
                Only schedule events ending on or before this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            active: String
                'yes', 'no' or 'both'. Default is 'both'.
                Only schedule events whose active state match the requested filter will be returned.

            active_users: Int
                '0', '-1' or '1' . Default is '1'.
                Only schedule events whose users are active will be returned by default.
                0 will return events for inactive users.
                -1 will return events for active and inactive users.

            draft: String
                'yes', 'no' or 'both'. Default is 'no'.
                Only schedule events whose draft state match the requested filter will be returned.

            team_events: String
                'base' or 'instance'. Default is 'instance'.
                If 'instance' is specified,
                events that are assigned to multiple users will be returned
                as individual single events for each assigned user. If 'base' is specified,
                events that are assigned to multiple users will be returned as one combined event
                for all assignees.

            modified_before: String
                required (unless ids, modified_since, or start are set)
                Only schedule events modified before this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            modified_since: String
                required (unless ids, modified_before, or start are set)
                Only schedule events modified since this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).

            supplemental_data: String
                'yes' or 'no'. Default is 'yes'.
                Indicates whether supplemental data should be returned.

            limit: Int
                Represents how many results you'd like to retrieve per request (page).
                Default is 200. Max is 200.

            page: Int
                Represents the page of results you'd like to retrieve. Default is 1.

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
        supplemental_data: Literal["yes", "no"] = "yes",
        limit=None,
        page=1,
    ):
        """
        This function allows you to call the /geolocations endpoint of the QuickBooksTime Time API.

        Args:
            ids: Int
                Comma separated list of one or more geolocation ids you'd like to filter on.
                Only geolocations with an id set to one of these values will be returned.
                Required (unless modified_before, modified_since is set)
            modified_before: String
                Only geolocations modified before this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).
                Required (unless ids or modified_since is set)
            modified_since: String
                Only geolocations modified since this date/time will be returned,
                in ISO 8601 format (YYYY-MM-DDThh:mm:ss±hh:mm).
                Required (unless ids or modified_before is set)
            user_ids: Int
                Comma separated list of one or more user ids you'd like to filter on.
                Only geolocations with a user id set to one of these values will be returned.
            group_ids: Int
                Comma separated list of one or more group ids you'd like to filter on.
                Only geolocations with a group id set to one of these values will be returned.
            suplemental_data: String
                'yes' or 'no'. Default is 'yes'.
                Indicates whether supplemental data should be returned.
            limit: Int
                Represents how many results you'd like to retrieve per request (page).
                Default is 200. Max is 200.
            page: Int
                Represents the page of results you'd like to retrieve. Default is 1.

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
