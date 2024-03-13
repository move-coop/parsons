"""NGPVAN Signups Endpoints"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class Signups(object):
    def __init__(self, van_connection):

        self.connection = van_connection

    def get_signups_statuses(self, event_id=None, event_type_id=None):
        """
        Get a list of valid signup statuses for a given event type
        or event. You must pass one of ``event_id`` or ``event_type_id``
        but not both.

        `Args:`
            event_id: int
                A valid event id.
            event_type_id: int
                A valid event type id.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        if event_id is None and event_type_id is None:
            raise ValueError("One of event_id or event_type_id must be populated")

        if event_id is not None and event_type_id is not None:
            raise ValueError("Event Id and Event Type ID may not BOTH be populated")

        if event_id:
            params = {"eventId": event_id}
        if event_type_id:
            params = {"eventTypeId": event_type_id}

        tbl = Table(self.connection.get_request("signups/statuses", params=params))
        logger.info(f"Found {tbl.num_rows} signups.")
        return tbl

    def get_person_signups(self, vanid):
        """
        Get the signup history of a person.

        `Args:`
            vanid: int
                A valid vanid associated with a person.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request("signups", params={"vanID": vanid}))
        logger.info(f"Found {tbl.num_rows} signups for {vanid}.")
        return self._unpack_signups(tbl)

    def get_event_signups(self, event_id):
        """
        Get the signup history of an event.

        `Args:`
            event_id: int
                A valid event_id associated with an event
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request("signups", params={"eventId": event_id}))
        logger.info(f"Found {tbl.num_rows} signups for event {event_id}.")
        return self._unpack_signups(tbl)

    def get_signup(self, event_signup_id):
        """
        Get a single signup object.

        `Args:`
            event_signup_id: int
                A valid event_signup_id associated with a signup.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        r = self.connection.get_request(f"signups/{event_signup_id}")
        logger.info(f"Found sign up {event_signup_id}.")
        return r

    def create_signup(self, vanid, event_id, shift_id, role_id, status_id, location_id):
        """
        Create a new signup for an event.

        `Args:`
            vanid: int
                A valid vanid of the person to signup for the event.
            event_id: int
                A valid event_id to associate the person with the event
            shift_id:
                A shift_id, associated with the event to assign the person
            role_id:
                A role_id, associated with the event to assign the person
            status_id:
                A status_id of the person
            location_id:
                A location_id for the event
        `Returns:`
            Int
                The event signup id
        """

        signup = {
            "person": {"vanId": vanid},
            "event": {"eventId": event_id},
            "shift": {"eventShiftId": shift_id},
            "role": {"roleId": role_id},
            "status": {"statusId": status_id},
            "location": {"locationId": location_id},
        }

        r = self.connection.post_request("signups", json=signup)
        logger.info(f"Signup {r} created.")
        return r

    def update_signup(
        self,
        event_signup_id,
        shift_id=None,
        role_id=None,
        status_id=None,
        location_id=None,
    ):
        """
        Update a signup object. All of the kwargs will update the values associated
        with them.

        `Args:`
            event_signup_id: int
                A valid event signup id
            shift_id: int
                The shift_id to update
            role_id: int
                The role_id to update
            status_id: int
                The status_id to update
            location_id: int
                The location_id to update
        `Returns:`
            ``None``
        """

        #  Get the signup object
        signup = self.connection.get_request(f"signups/{event_signup_id}")

        # Update the signup object
        if shift_id:
            signup["shift"] = {"eventShiftId": shift_id}
        if role_id:
            signup["role"] = {"roleId": role_id}
        if status_id:
            signup["status"] = {"statusId": status_id}
        if location_id:
            signup["location"] = {"locationId": location_id}

        return self.connection.put_request(f"signups/{event_signup_id}", json=signup)

    def delete_signup(self, event_signup_id):
        """
        Delete a signup object

        `Args:`
            event_signup_id: int
                A valid event signup id
        `Returns:`
            ``None``
        """

        r = self.connection.delete_request(f"signups/{event_signup_id}")
        logger.info(f"Signup {event_signup_id} deleted.")
        return r

    def _unpack_signups(self, table):

        # Unpack all of the nested jsons
        table.unpack_dict("person", prepend=False)
        table.unpack_dict("status")
        table.unpack_dict("event")
        table.unpack_dict("shift")
        table.unpack_dict("role")
        table.unpack_dict("location")

        return table
