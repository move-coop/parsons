import logging

logger = logging.getLogger(__name__)

class Events:
    """A class for interacting with PDI events via PDIs API"""

    def __init__(self):
        self.events_url = self.base_url + '/events'
        self.calendars_url = self.base_url + '/calendars'
        self.eventactivities_url = self.base_url + '/eventActivities'

        super().__init__()

    def create_event(self, calendar_id: str, location_id: str, event_name: str, start_datetime: str,
                     end_datetime: str, description=None,all_day=False, recurrencetype=None,
                     recurrence_end_datetime=None, host_phone=None, host_email=None, website=None):
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
          "website": website
        }

        response = self._request(self.calendars_url + f'/{calendar_id}' + '/events',
                                 req_type='POST', post_data=payload)
        event_id = response['id']
        logger.info(f'Created event {event_name} (id: {event_id})')

        return response

    def create_event_with_activity(self, calendar_id: str, location_id: str, activity_id: str,
                                   event_name: str, activity_name: str, start_datetime: str,
                                   end_datetime: str, description=None, all_day=False,
                                   recurrencetype=None, recurrence_end_datetime=None, host_phone=None,
                                   host_email=None, website=None, signup_goal=None):
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
                    """
        event_data = self.create_event(calendar_id, location_id, event_name, start_datetime,
                                       end_datetime, description, all_day, recurrencetype,
                                       recurrence_end_datetime, host_phone, host_email, website)
        event_id = event_data['id']
        logger.info(f'Created event {event_name} (id: {event_id})')

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
            "RecurrenceEndDateTimeUtc": recurrence_end_datetime
        }

        response = self._request(self.eventactivities_url, req_type='POST',
                                 post_data=event_activity_payload)
        logger.info(f'Created activity {activity_name} for event {event_name} (id: {event_id})')

        return response

    def create_event_activity(self, calendar_id: str, event_id: str, activity_id: str,
                              location_id: str, activity_name: str, start_datetime: str,
                              end_datetime: str, description=None, recurrencetype=None,
                              recurrence_end_datetime=None, signup_goal=None):
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
            "RecurrenceEndDateTimeUtc": recurrence_end_datetime
        }

        response = self._request(self.eventactivities_url, req_type='POST',
                                 post_data=event_activity_payload)
        logger.info(f'Created activity {activity_name} for event {event_id})')

        return response