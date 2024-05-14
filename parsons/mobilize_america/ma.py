from requests import request as _request
from parsons.etl.table import Table
from parsons.utilities.datetime import date_to_timestamp
import petl
import re
import os
import logging
import collections.abc

logger = logging.getLogger(__name__)

MA_URI = "https://api.mobilize.us/v1/"


class MobilizeAmerica(object):
    """
    Instantiate MobilizeAmerica Class

    api_key: str
        An api key issued by Mobilize America. This is required to access some private methods.

    `Returns:`
        MobilizeAmerica Class
    """

    def __init__(self, api_key=None):

        self.uri = MA_URI
        self.api_key = api_key or os.environ.get("MOBILIZE_AMERICA_API_KEY")

        if not self.api_key:
            logger.info(
                "Mobilize America API Key missing. Calling methods that rely on private"
                " endpoints will fail."
            )

    def _request(self, url, req_type="GET", post_data=None, args=None, auth=False):
        if auth:

            if not self.api_key:
                raise TypeError("This method requires an api key.")
            else:
                header = {"Authorization": "Bearer " + self.api_key}

        else:
            header = None

        r = _request(req_type, url, json=post_data, params=args, headers=header)

        r.raise_for_status()

        if "error" in r.json():
            raise ValueError("API Error:" + str(r.json()["error"]))

        return r

    def _request_paginate(self, url, req_type="GET", args=None, auth=False):

        r = self._request(url, req_type=req_type, args=args, auth=auth)

        json = r.json()["data"]

        while r.json()["next"]:

            r = self._request(r.json()["next"], req_type=req_type, auth=auth)
            json.extend(r.json()["data"])

        return json

    def _time_parse(self, time_arg):
        # Parse the date filters

        trans = [(">=", "gte_"), (">", "gt_"), ("<=", "lte_"), ("<", "lt_")]

        if time_arg:

            time = re.sub("<=|<|>=|>", "", time_arg)
            time = date_to_timestamp(time)
            time_filter = re.search("<=|<|>=|>", time_arg).group()

            for i in trans:
                if time_filter == i[0]:
                    return i[1] + str(time)

            raise ValueError("Invalid time operator. Must be one of >=, >, <= or >.")

        return time_arg

    def get_organizations(self, updated_since=None):
        """
        Return all active organizations on the platform.

        `Args:`
            updated_since: str
                Filter to organizations updated since given date (ISO Date)
        `Returns`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        return Table(
            self._request_paginate(
                self.uri + "organizations",
                args={"updated_since": date_to_timestamp(updated_since)},
            )
        )

    def get_promoted_organizations(self, organization_id):
        """
        Return all organizations promoted by the given organization.

        `Args:`
            organization_id: int
                ID of the organization to query.
        `Returns`
            Parsons Table
        """
        url = self.uri + "organizations/" + str(organization_id) + "/promoted_organizations"
        return Table(self._request_paginate(url, auth=True))

    def get_events(
        self,
        organization_id=None,
        updated_since=None,
        timeslot_start=None,
        timeslot_end=None,
        timeslots_table=False,
        max_timeslots=None,
    ):
        """
        Fetch all public events on the platform.

        `Args:`
            organization_id: list or int
                Filter events by a single or multiple organization ids
            updated_since: str
                Filter to events updated since given date (ISO Date)
            timeslot_start: str
                Filter by a timeslot start of events using ``>``,``>=``,``<``,``<=``
                operators and ISO date (ex. ``<=2018-12-13 05:00:00PM``)
            timeslot_end: str
                Filter by a timeslot end of events using ``>``,``>=``,``<``,``<=``
                operators and ISO date (ex. ``<=2018-12-13 05:00:00PM``)
            timeslot_table: boolean
                Return timeslots as a separate long table. Useful for extracting
                to databases.
            max_timeslots: int
                If not returning a timeslot table, will unpack time slots. If do not
                set this kwarg, it will add a column for each time slot. The argument
                limits the number of columns and discards any additional timeslots
                after that.

                For example: If there are 20 timeslots associated with your event,
                and you set the max time slots to 5, it will only return the first 5
                time slots as ``time_slot_0``, ``time_slot_1`` etc.

                This is helpful in situations where you have a regular sync
                running and want to ensure that the column headers remain static.

                If ``max_timeslots`` is 0, no timeslot columns will be included.

        `Returns`
            :ref:`parsons.Table <parsons-table>`, dict, list[:ref:`parsons.Table <parsons-table>`]
        """

        if isinstance(organization_id, (str, int)):
            organization_id = [organization_id]

        args = {
            "organization_id": organization_id,
            "updated_since": date_to_timestamp(updated_since),
            "timeslot_start": self._time_parse(timeslot_start),
            "timeslot_end": self._time_parse(timeslot_end),
        }

        tbl = Table(self._request_paginate(self.uri + "events", args=args))

        if tbl.num_rows > 0:

            tbl.unpack_dict("sponsor")
            tbl.unpack_dict("location", prepend=False)
            tbl.unpack_dict("location", prepend=False)  # Intentional duplicate
            tbl.table = petl.convert(tbl.table, "address_lines", lambda v: " ".join(v))

            if timeslots_table:

                timeslots_tbl = tbl.long_table(["id"], "timeslots", "event_id")
                return {"events": tbl, "timeslots": timeslots_tbl}

            elif max_timeslots == 0:
                tbl.remove_column("timeslots")

            else:
                tbl.unpack_list("timeslots", replace=True, max_columns=max_timeslots)
                cols = tbl.columns
                for c in cols:
                    if re.search("timeslots", c, re.IGNORECASE) is not None:
                        tbl.unpack_dict(c)
                        tbl.materialize()

        return tbl

    def get_events_organization(
        self,
        organization_id,
        updated_since=None,
        timeslot_start=None,
        timeslot_end=None,
        timeslots_table=False,
        max_timeslots=None,
    ):
        """
        Fetch all public events for an organization. This includes both events owned
        by the organization (as indicated by the organization field on the event object)
        and events of other organizations promoted by this specified organization.

        .. note::
            API Key Required

        `Args:`
            organization_id: int or str
                Organization ID for the organization.
            updated_since: str
                Filter to events updated since given date (ISO Date)
            timeslot_start: str
                Filter by a timeslot start of events using ``>``,``>=``,``<``,``<=``
                operators and ISO date (ex. ``<=2018-12-13 05:00:00PM``)
            timeslot_end: str
                Filter by a timeslot end of events using ``>``,``>=``,``<``,``<=``
                operators and ISO date (ex. ``<=2018-12-13 05:00:00PM``)
            timeslot_table: boolean
                Return timeslots as a separate long table. Useful for extracting
                to databases.
            zipcode: str
                Filter by a Events' Locations' postal code. If present, returns Events
                sorted by distance from zipcode. If present, virtual events will not be returned.
            max_dist: str
                Filter Events' Locations' distance from provided zipcode.
            visibility: str
                Either `PUBLIC` or `PRIVATE`. Private events only return if user is authenticated;
                if `visibility=PRIVATE` and user doesn't have permission, no events returned.
            exclude_full: bool
                If `exclude_full=true`, filter out full Timeslots (and Events if all of an Event's
                Timeslots are full)
            is_virtual: bool
                `is_virtual=false` will return only in-person events, while `is_virtual=true` will
                return only virtual events. If excluded, return virtual and in-person events. Note
                that providing a zipcode also implies `is_virtual=false`.
            event_types:enum
                The type of the event, one of: `CANVASS`, `PHONE_BANK`, `TEXT_BANK`, `MEETING`,
                `COMMUNITY`, `FUNDRAISER`, `MEET_GREET`, `HOUSE_PARTY`, `VOTER_REG`, `TRAINING`,
                `FRIEND_TO_FRIEND_OUTREACH`, `DEBATE_WATCH_PARTY`, `ADVOCACY_CALL`, `OTHER`.
                This list may expand in the future.
            max_timeslots: int
                If not returning a timeslot table, will unpack time slots. If do not
                set this arg, it will add a column for each time slot. The argument
                limits the number of columns and discards any additional timeslots
                after that.

                For example: If there are 20 timeslots associated with your event,
                and you set the max time slots to 5, it will only return the first 5
                time slots as ``time_slot_0``, ``time_slot_1`` etc.

                This is helpful in situations where you have a regular sync
                running and want to ensure that the column headers remain static.

                If ``max_timeslots`` is 0, no timeslot columns will be included.

        `Returns`
            :ref:`parsons.Table <parsons-table>`, dict, list[:ref:`parsons.Table <parsons-table>`]
        """

        args = {
            "updated_since": date_to_timestamp(updated_since),
            "timeslot_start": self._time_parse(timeslot_start),
            "timeslot_end": self._time_parse(timeslot_end),
        }

        tbl = Table(
            self._request_paginate(
                self.uri + "organizations/" + str(organization_id) + "/events",
                args=args,
                auth=True,
            )
        )

        if tbl.num_rows > 0:

            tbl.unpack_dict("sponsor")
            tbl.unpack_dict("location", prepend=False)
            tbl.unpack_dict("location", prepend=False)  # Intentional duplicate
            tbl.table = petl.convert(tbl.table, "address_lines", lambda v: " ".join(v))

            if timeslots_table:

                timeslots_tbl = tbl.long_table(["id"], "timeslots", "event_id")
                return {"events": tbl, "timeslots": timeslots_tbl}

            elif max_timeslots == 0:
                tbl.remove_column("timeslots")

            else:
                tbl.unpack_list("timeslots", replace=True, max_columns=max_timeslots)
                cols = tbl.columns
                for c in cols:
                    if re.search("timeslots", c, re.IGNORECASE) is not None:
                        tbl.unpack_dict(c)
                        tbl.materialize()

        return tbl

    def get_events_deleted(self, organization_id=None, updated_since=None):
        """
        Fetch deleted public events on the platform.

        `Args:`
            organization_id: list or int
                Filter events by a single or multiple organization ids
            updated_since: str
                Filter to events updated since given date (ISO Date)
        `Returns`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        if isinstance(organization_id, (str, int)):
            organization_id = [organization_id]

        args = {
            "organization_id": organization_id,
            "updated_since": date_to_timestamp(updated_since),
        }

        return Table(self._request_paginate(self.uri + "events/deleted", args=args))

    def get_people(self, organization_id, updated_since=None):
        """
        Fetch all people (volunteers) who are affiliated with an organization(s).

        .. note::
            API Key Required

        `Args:`
            organization_id: Iterable or int
                Request people associated with a single or multiple organization ids
            updated_since: str
                Filter to people updated since given date (ISO Date)
        `Returns`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        if isinstance(organization_id, collections.abc.Iterable):
            data = Table()
            for id in organization_id:
                data.concat(self.get_people(id, updated_since))
            return data
        else:
            url = self.uri + "organizations/" + str(organization_id) + "/people"
            args = {"updated_since": date_to_timestamp(updated_since)}
            return Table(self._request_paginate(url, args=args, auth=True))

    def get_attendances(self, organization_id, updated_since=None):
        """
        Fetch all attendances which were either promoted by the organization or
        were for events owned by the organization.

        .. note::
            API Key Required

        `Args:`
            organization_id: int
                Filter attendances by an organization id
            updated_since: str
                Filter to attendances updated since given date (ISO Date)
        `Returns`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.uri + "organizations/" + str(organization_id) + "/attendances"
        args = {"updated_since": date_to_timestamp(updated_since)}
        return Table(self._request_paginate(url, args=args, auth=True))
