class Events:
    """A class for interacting with PDI events via PDIs API"""

    def __init__(self):
        self.events_url = self.base_url + '/events'
        self.calendars_url = self.base_url + '/calendars'

        super().__init__()

    def create_event(self, calendar_id: str, location_id: str, name: str, start_date: str,
                     end_date: str, description=None,all_day=False, recurrencetype=None,
                     recurrence_end_date=None, host_phone=None, host_email=None, website=None):
        """Create event in a specified calendar

        `Args:`
            location_id: str
                The unique ID of the PDI location this event took place/is to take place at
            name: str
                The name of your event
            description: str
                A short description for your event
            start_date: str
                The start datetime of the event in UTC timezone formatted as
                yyyy-MM-ddThh:mm:ss.fffZ
            end_date: str
                The end date formatted like start_date
            is_all_day = bool
                set to True if event is an all day event. Defaults to False
            recurrencetype: str
                Either 'daily', 'weekly', or 'monthly'. Defaults to None
            recurrence_end_date: str
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
          "name": name,
          "description": description,
          "startDateTimeUtc": start_date,
          "endDateTimeUtc": end_date,
          "isAllDay": str(all_day).lower(),
          "recurrenceEndDateTimeUtc": recurrence_end_date,
          "phone": host_phone,
          "contactEmail": host_email,
          "website": website
                    }

        response = self._request(self.calendars_url + f'/{calendar_id}' + '/events',
                                 req_type='POST', post_data=payload)
        return response