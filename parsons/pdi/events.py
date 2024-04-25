import logging

logger = logging.getLogger(__name__)


class Events:
    """A class for interacting with PDI events via PDIs API"""

    def __init__(self):
        self.events_url = self.base_url + "/events"
        self.calendars_url = self.base_url + "/calendars"
        self.eventactivities_url = self.base_url + "/eventActivities"
        self.activites_url = self.base_url + "/activities"
        self.activityassignment_url = self.base_url + "/eventActivityAssignments"

        super().__init__()

    def get_events(self, first_event_date: str, last_event_date: str, limit=None):
        """Get a table of PDI events in a given time frame

        `Args:`
            first_event_date: str
                First date in the timeframe from which you want events formatted at 'yyy-MM-dd'
            last_event_date: str
                Last date in the timeframe from which you want events formatted at 'yyy-MM-dd'
            limit: int
                The max number of events to return

        `Returns:`
            parsons.Table
                A Parsons table containing all requested events data.
        """

        params = {
            "startDate": first_event_date,
            "endDate": last_event_date,
        }

        return self._request(self.events_url, args=params, limit=limit)

    def get_event_invitations(self, event_id: str, expand=True, limit=None):
        """Get a table of PDI event invitations for a specified event

        `Args:`
            event_id: str
                ID of event for which you want invitations
            expand: bool
                If True returns columns for contact (and all contact info) and event)

        `Returns:`
            parsons.Table
                A Parsons table containing all requested event invitation data.
        """

        params = {"expand": expand}

        return self._request(f"{self.events_url}/{event_id}/invitations", args=params, limit=limit)

    def create_event(
        self,
        calendar_id: str,
        location_id: str,
        event_name: str,
        start_datetime: str,
        end_datetime: str,
        description=None,
        all_day=False,
        recurrencetype=None,
        recurrence_end_datetime=None,
        host_phone=None,
        host_email=None,
        website=None,
    ):
        """Create event in a specified calendar

        `Args:`
            calendar_id: str
                The calendar in which you'd like to create an event
            location_id: str
                The unique ID of the PDI location this event took place/is to take place at
            event_name: str
                The name of your event
            description: str
                A short description for your event
            start_datetime: str
                The start datetime of the event in UTC timezone formatted as
                yyyy-MM-ddThh:mm:ss.fffZ
            end_datetime: str
                The end date formatted like start_datetime
            is_all_day: bool
                set to True if event is an all day event. Defaults to False
            recurrencetype: str
                Either 'daily', 'weekly', or 'monthly'. Defaults to None
            recurrence_end_datetime: str
                The end time of the last recurrence of the event formatted as
                yyyy-MM-ddThh:mm:ss.fffZ
            host_phone: str
                An optional contact phone number for the host. Defaults to None
            host_email: str
                An optional contact email for the host. Defaults to None
            website: str
                An optional website for the event. Defualts to None

        `Returns:`
            dict
                Response from PDI in dictionary object

        """

        payload = {
            "locationId": location_id,
            "recurrenceType": recurrencetype,
            "name": event_name,
            "description": description,
            "startDateTimeUtc": start_datetime,
            "endDateTimeUtc": end_datetime,
            "isAllDay": str(all_day).lower(),
            "recurrenceEndDateTimeUtc": recurrence_end_datetime,
            "phone": host_phone,
            "contactEmail": host_email,
            "website": website,
        }

        response = self._request(
            self.calendars_url + f"/{calendar_id}" + "/events",
            req_type="POST",
            post_data=payload,
        )
        event_id = response["id"]
        logger.info(f"Created event {event_name} (id: {event_id})")

        return response

    def create_event_with_activity(
        self,
        calendar_id: str,
        location_id: str,
        activity_id: str,
        event_name: str,
        activity_name: str,
        start_datetime: str,
        end_datetime: str,
        description=None,
        all_day=False,
        recurrencetype=None,
        recurrence_end_datetime=None,
        host_phone=None,
        host_email=None,
        website=None,
        signup_goal=None,
    ):
        """Create event in a specified calendar with an associated activity. The activty will
        be assigned the same start, end time, and recurrance settings as the event.

            `Args:`
                calendar_id: str
                    The unique ID of the calendar in which you'd like to create an event
                location_id: str
                    The unique ID of the PDI location whek this event took place/is to take
                    place
                activity_id:
                    The unique ID of the activity type you'd like to add to the event
                event_name: str
                    The name of your event
                activity_name: str
                    The name of your activity. e.g. 'Pictionary!'
                description: str
                    A short description for your event
                start_datetime: str
                    The start datetime of the event in UTC timezone formatted as
                    yyyy-MM-ddThh:mm:ss.fffZ
                end_datetime: str
                    The end date formatted like start_datetime
                is_all_day = bool
                    set to True if event is an all day event. Defaults to False
                recurrencetype: str
                    Either 'daily', 'weekly', or 'monthly'. Defaults to None
                recurrence_end_datetime: str
                    The end time of the last recurrence of the event formatted as
                    yyyy-MM-ddThh:mm:ss.fffZ
                host_phone: str
                    An optional contact phone number for the host. Defaults to None
                host_email: str
                    An optional contact email for the host. Defaults to None
                website: str
                    An optional website for the event. Defualts to None
                signup_goal: int
                    The goal of how many people you want to complete the activity
            `Returns:`
                dict
                    Response from PDI in dictionary object
        """
        event_data = self.create_event(
            calendar_id,
            location_id,
            event_name,
            start_datetime,
            end_datetime,
            description,
            all_day,
            recurrencetype,
            recurrence_end_datetime,
            host_phone,
            host_email,
            website,
        )
        event_id = event_data["id"]
        logger.info(f"Created event {event_name} (id: {event_id})")

        event_activity_payload = {
            "CalendarId": calendar_id,
            "EventId": event_id,
            "ActivityId": activity_id,
            "LocationId": location_id,
            "RecurrenceType": recurrencetype,
            "Name": activity_name,
            "Description": None,
            "StartDateTimeUtc": start_datetime,
            "EndDateTimeUtc": end_datetime,
            "CountGoal": signup_goal,
            "RecurrenceEndDateTimeUtc": recurrence_end_datetime,
        }

        response = self._request(
            self.eventactivities_url, req_type="POST", post_data=event_activity_payload
        )
        logger.info(f"Created activity {activity_name} for event {event_name} (id: {event_id})")

        return response

    def create_event_activity(
        self,
        calendar_id: str,
        event_id: str,
        activity_id: str,
        location_id: str,
        activity_name: str,
        start_datetime: str,
        end_datetime: str,
        description=None,
        recurrencetype=None,
        recurrence_end_datetime=None,
        signup_goal=None,
    ):
        """Create event in a specified calendar with an associated activity

        `Args:`
            calendar_id: str
                The unique ID of the calendar in which you'd like to create an event
            event_id: str
                The unique ID of the event this activity is to be associated with
            activity_id:
                The unique ID of the activity type you'd like to add to the event
            location_id: str
                The unique ID of the PDI location where this event took place/is to take
                place
            activity_name: str
                The name of your activity. e.g. 'Pictionary!'
            description: str
                A short description for your event activity
            start_datetime: str
                The start datetime of the event in UTC timezone formatted as
                yyyy-MM-ddThh:mm:ss.fffZ
            end_datetime: str
                The end date formatted like start_datetime
            recurrencetype: str
                Either 'daily', 'weekly', or 'monthly'. Defaults to None
            recurrence_end_datetime: str
                The end time of the last recurrence of the event formatted as
                yyyy-MM-ddThh:mm:ss.fffZ
            signup_goal: int
                The goal of how many people you want to complete the activity


        `Returns:`
            dict
                Response from PDI in dictionary object
        """

        event_activity_payload = {
            "CalendarId": calendar_id,
            "EventId": event_id,
            "ActivityId": activity_id,
            "LocationId": location_id,
            "RecurrenceType": recurrencetype,
            "Name": activity_name,
            "Description": description,
            "StartDateTimeUtc": start_datetime,
            "EndDateTimeUtc": end_datetime,
            "CountGoal": signup_goal,
            "RecurrenceEndDateTimeUtc": recurrence_end_datetime,
        }

        response = self._request(
            self.eventactivities_url, req_type="POST", post_data=event_activity_payload
        )
        logger.info(f"Created activity {activity_name} for event {event_id})")

        return response

    def create_invitation(
        self,
        event_id: str,
        contact_id: str,
        status: str,
        attended: bool,
        confirmed=False,
        specific_occurrence_start=None,
    ):
        """Create a PDI event invitation indicating a contact has been registered for an event
        `Args:`
            event_id: str
                The ID of the event to write the RSVP to
            contact_id: str
                The ID of the contact to which the invitation belongs
            status: str
                Options are: "Yes", "No", "Maybe", "Scheduled", "Invited", "Cancelled",
                "No-Show", "Completed", and ""
            attended: boolean
                Indicates whether contact attended event
            confirmed: boolean
                Indicates whether invitation confirmed they will attend the event. Defaults to
                False
            specific_occurrence_start: str
                If invitation is for a specific occurrence of a recurring event, then the start
                datetime of the event in UTC formatted as yyyy-MM-ddTHH:mm:ss.fffZ
        `Returns:`
            dict
                Response from PDI in dictionary object
        """

        event_invitation_payload = {
            "contactId": contact_id,
            "rsvpStatus": status,
            "isConfirmed": confirmed,
            "attended": attended,
        }

        if specific_occurrence_start:
            event_invitation_payload["specificOcurrenceStartUtc"] = specific_occurrence_start

        response = self._request(
            self.events_url + f"/{event_id}/invitations",
            req_type="POST",
            post_data=event_invitation_payload,
        )
        return response

    def update_invitation(
        self,
        invitation_id: str,
        event_id: str,
        contact_id: str,
        status=None,
        attended=None,
        confirmed=None,
        specific_occurrence_start=None,
    ):
        """Modify a PDI event invitation
        `Args:`
            invitation_id: str
                The ID of the event invitation
            event_id: str
                The ID of the event that corresponds to the invitation
            contact_id: str
                The ID of the contact to which the invitation belongs
            status: str
                Options are: "Yes", "No", "Maybe", "Scheduled", "Invited", "Cancelled",
                "No-Show", "Completed", and ""
            attended: boolean
                Indicates whether contact attended event
            confirmed: boolean
                Indicates whether invitation confirmed they will attend the event
            specific_occurrence_start: str
                If invitation is for a specific occurrence of a recurring event, then the start
                datetime of the event in UTC formatted as yyyy-MM-ddTHH:mm:ss.fffZ
        `Returns:`
            dict
                Response from PDI in dictionary object
        """

        event_invitation_payload = {"contactId": contact_id}

        if status:
            event_invitation_payload["rsvpStatus"] = status
        if confirmed is not None:
            event_invitation_payload["isConfirmed"] = confirmed
        if attended is not None:
            event_invitation_payload["attended"] = attended
        if specific_occurrence_start:
            event_invitation_payload["specificOcurrenceStartUtc"] = specific_occurrence_start

        response = self._request(
            self.events_url + f"/{event_id}/invitations/{invitation_id}",
            req_type="PUT",
            post_data=event_invitation_payload,
        )
        return response

    def create_activity_assignment(
        self,
        eventactivityid: str,
        contact_id: str,
        status: str,
        completed: bool,
        confirmed=False,
        specific_occurrence_start=None,
    ):
        """Create an activity assignement
        `Args:`
            eventactivityid: str
                The ID of the specific event activity you'd like to assign a contact
            contact_id: str
                The ID of the contact to which the assignment belongs
            status: str
                Options are: "Yes", "No", "Maybe", "Scheduled", "Invited", "Cancelled",
                "No-Show", "Completed", and ""
            completed: boolean
                Indicates whether contact attended event
            confirmed: boolean
                Indicates whether invitation confirmed they will attend the event
            specific_occurrence_start: str
                If invitation is for a specific occurrence of a recurring event, then the start
                datetime of the event in UTC formatted as yyyy-MM-ddTHH:mm:ss.fffZ
        `Returns:`
            dict
                Response from PDI in dictionary object
        """

        assignment_payload = {
            "rsvpStatus": status,
            "isConfirmed": confirmed,
            "isShiftWorked": completed,
            "contactId": contact_id,
            "eventActivityId": eventactivityid,
        }

        if specific_occurrence_start:
            assignment_payload["specificOcurrenceStartUtc"] = specific_occurrence_start

        response = self._request(
            self.activityassignment_url, req_type="POST", post_data=assignment_payload
        )

        return response

    def update_activity_assignment(
        self,
        activityassignementid: str,
        eventactivityid: str,
        contact_id: str,
        status=None,
        completed=None,
        confirmed=None,
        specific_occurrence_start=None,
    ):
        """Create an activity assignement
        `Args:`
            activityassignementid: str
                Id of the specific event activity assignement you want to modify
            eventactivityid: str
                The ID of the specific event activity you'd like to assign a contact
            contact_id: str
                The ID of the contact to which the assignment belongs
            status: str
                Options are: "Yes", "No", "Maybe", "Scheduled", "Invited", "Cancelled",
                "No-Show", "Completed", and ""
            completed: boolean
                Indicates whether contact attended event
            confirmed: boolean
                Indicates whether invitation confirmed they will attend the event
            specific_occurrence_start: str
                If invitation is for a specific occurrence of a recurring event, then the start
                datetime of the event in UTC formatted as yyyy-MM-ddTHH:mm:ss.fffZ
        `Returns:`
            dict
                Response from PDI in dictionary object
        """

        assignment_payload = {
            "contactId": contact_id,
            "eventActivityId": eventactivityid,
        }

        if status:
            assignment_payload["rsvpStatus"] = status
        if confirmed is not None:
            assignment_payload["isConfirmed"] = confirmed
        if completed is not None:
            assignment_payload["isShiftWorked"] = completed
        if specific_occurrence_start:
            assignment_payload["specificOcurrenceStartUtc"] = specific_occurrence_start

        response = self._request(
            self.activityassignment_url + f"/{activityassignementid}",
            req_type="PUT",
            post_data=assignment_payload,
        )

        return response

    def get_event_activity_assignments(self, start_date, end_date, expand, limit=None):
        """
        Get a list of event activity assignments.
        Relevant API docs:
            https://api.bluevote.com/docs/index#/EventActivityAssignments

        `Args`:
            start_date: str
                Earliest records to be returned in the API response
                Per the API docs, use "YYYY-MM-DD" format

            end_date: str
                Latest records to be returned in the API response.
                Per the API docs, use "YYYY-MM-DD" format

            expand: bool
                Parameter to determine if we return the list of shift assigments
                expanded or not

            limit: int
                Specify limit to return (max=2000)

        `Returns`:
            Parsons Table with event activity assignment responses
        """

        if limit and limit > 2000:
            raise ValueError("Maximum allowed limit is 2000")

        params = {"startDate": start_date, "endDate": end_date, "expand": expand}
        return self._request(self.activityassignment_url, args=params, limit=limit)

    def get_event_activities(self, start_date, end_date, limit=None):
        """
        Get a list of event activities.
        Relevant API docs:
            https://api.bluevote.com/docs/index#!/EventActivities/EventActivities_GetAll

        `Args`:
            start_date: str
                Earliest records to be returned in the API response
                Per the API docs, use "YYYY-MM-DD" format

            end_date: str
                Latest records to be returned in the API response.
                Per the API docs, use "YYYY-MM-DD" format

            limit: int
                Specify limit to return (max=2000)

        `Returns`:
            Parsons Table with event activity responses
        """

        if limit and limit > 2000:
            raise ValueError("Maximum allowed limit is 2000")

        params = {"startDate": start_date, "endDate": end_date}
        return self._request(self.eventactivities_url, args=params, limit=limit)

    def get_calendars(self, limit=None):
        """
        Gets a list of calendars.
        Relevant API docs:
            https://api.bluevote.com/docs/index#!/Calendars/Calendars_GetAll

        `Args`:
            limit: int
                Specify limit to return (max=2000)

        `Returns`:
            Parsons Table object with id, name, description, and timeZone records
        """

        if limit and limit > 2000:
            raise ValueError("Maximum allowed limit is 2000")

        return self._request(self.calendars_url, limit=limit)
