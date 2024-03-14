import unittest
import os
import requests_mock
from parsons import VAN
from test.utils import validate_list

signup_status = [
    {"statusId": 5, "name": "Cancelled"},
    {"statusId": 2, "name": "Completed"},
    {"statusId": 11, "name": "Confirmed"},
    {"statusId": 4, "name": "Invited"},
    {"statusId": 18, "name": "Left Msg"},
    {"statusId": 6, "name": "No Show"},
    {"statusId": 1, "name": "Scheduled"},
    {"statusId": 30, "name": "Sched-Web"},
    {"statusId": 15, "name": "Walk In"},
]

signup = {
    "eventSignupId": 14285,
    "person": {
        "vanId": 100349920,
        "firstName": "Helen",
        "middleName": None,
        "lastName": "Maddix",
        "contactOrganizationCommonName": None,
        "contactOrganizationOfficialName": None,
        "contactModeId": 1,
        "email": None,
        "phone": None,
    },
    "event": {"eventId": 750001004, "name": "Canvass 01", "shortName": "Can01"},
    "shift": {"eventShiftId": 19076, "name": "Default Shift"},
    "role": {"roleId": 263920, "name": "Leader"},
    "status": {"statusId": 11, "name": "Confirmed"},
    "location": {
        "locationId": 3,
        "name": "First Presbyterian Church",
        "displayName": "First Presbyterian Church, 340 5th Ave S Saint Cloud, MN 56301 ",
    },
    "startTimeOverride": "2018-12-31T08:00:00-05:00",
    "endTimeOverride": "2018-12-31T10:00:00-05:00",
    "printedLists": None,
    "minivanExports": None,
    "supporterGroupId": None,
    "isOfflineSignup": True,
}

signup_expected = [
    "eventSignupId",
    "startTimeOverride",
    "endTimeOverride",
    "printedLists",
    "minivanExports",
    "supporterGroupId",
    "isOfflineSignup",
    "contactModeId",
    "contactOrganizationCommonName",
    "contactOrganizationOfficialName",
    "email",
    "firstName",
    "lastName",
    "middleName",
    "phone",
    "vanId",
    "status_name",
    "status_statusId",
    "event_eventId",
    "event_name",
    "event_shortName",
    "shift_eventShiftId",
    "shift_name",
    "role_name",
    "role_roleId",
    "location_displayName",
    "location_locationId",
    "location_name",
]

os.environ["VAN_API_KEY"] = "SOME_KEY"


class TestSignups(unittest.TestCase):
    def setUp(self):

        self.van = VAN(os.environ["VAN_API_KEY"], db="EveryAction", raise_for_status=False)

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_get_signup_statuses(self, m):

        m.get(self.van.connection.uri + "signups/statuses", json=signup_status)

        # Test events lookup
        self.assertTrue(
            validate_list(["statusId", "name"], self.van.get_signups_statuses(event_id=750000849))
        )

        # Test event type lookup
        self.assertTrue(
            validate_list(
                ["statusId", "name"],
                self.van.get_signups_statuses(event_type_id=750000849),
            )
        )

    @requests_mock.Mocker()
    def test_get_signups(self, m):

        json = {"items": [signup], "nextPageLink": None, "count": 1}

        m.get(self.van.connection.uri + "signups", json=json)

        self.assertTrue(
            validate_list(signup_expected, self.van.get_event_signups(event_id=750001004))
        )

        self.assertTrue(
            validate_list(signup_expected, self.van.get_person_signups(vanid=750000849))
        )

    @requests_mock.Mocker()
    def test_get_signup(self, m):

        event_signup_id = 14285

        m.get(self.van.connection.uri + f"signups/{event_signup_id}".format(), json=signup)

        self.assertEqual(signup, self.van.get_signup(event_signup_id))

    @requests_mock.Mocker()
    def test_create_signup(self, m):

        m.post(self.van.connection.uri + "signups", json=14285, status_code=201)

        self.assertEqual(self.van.create_signup(100349920, 750001004, 19076, 263920, 11, 3), 14285)

    @requests_mock.Mocker()
    def test_update_signup(self, m):

        # This is two part. It makes a call to get the object and then it updates it

        event_signup_id = 14285

        # Get object route
        m.get(self.van.connection.uri + f"signups/{event_signup_id}", json=signup)

        # Update object
        m.put(self.van.connection.uri + f"signups/{event_signup_id}", status_code=204)

        self.van.update_signup(event_signup_id, status_id=6)
