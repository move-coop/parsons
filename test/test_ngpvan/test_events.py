import os
import unittest

import requests_mock

from parsons import VAN
from test.conftest import validate_list

os.environ["VAN_API_KEY"] = "SOME_KEY"


class TestNGPVAN(unittest.TestCase):
    def setUp(self):
        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters")

    def tearDown(self):
        pass

    @requests_mock.Mocker()
    def test_get_events(self, m):
        json = {
            "count": 6,
            "items": [
                {
                    "eventId": 1062,
                    "startDate": "2010-05-25T11:00:00-05:00",
                    "codes": "null",
                    "endDate": "2010-05-25T15:00:00-05:00",
                    "name": "Sample",
                    "roles": "null",
                    "isOnlyEditableByCreatingUser": "true",
                    "ticketCategories": "null",
                    "eventType": {"eventTypeId": 29166, "name": "Confirmation Calls"},
                    "notes": "null",
                    "districtFieldValue": "null",
                    "locations": "null",
                    "shifts": "null",
                    "voterRegistrationBatches": "null",
                    "createdDate": "2010-05-25T11:55:00Z",
                    "financialProgram": "null",
                    "shortName": "Sample",
                    "isPubliclyViewable": "null",
                    "isActive": "true",
                    "description": "This is a sample",
                }
            ],
            "nextPageLink": None,
        }

        m.get(self.van.connection.uri + "events", json=json)

        # Expected Structure
        expected = [
            "eventId",
            "startDate",
            "codes",
            "endDate",
            "name",
            "roles",
            "isOnlyEditableByCreatingUser",
            "ticketCategories",
            "eventType",
            "notes",
            "districtFieldValue",
            "locations",
            "shifts",
            "voterRegistrationBatches",
            "createdDate",
            "financialProgram",
            "shortName",
            "isPubliclyViewable",
            "isActive",
            "description",
        ]

        assert validate_list(expected, self.van.get_events())

    @requests_mock.Mocker()
    def test_get_events_pagination_does_not_duplicate_params(self, m):
        # VAN's `nextPageLink` is a fully-formed URL that already carries the
        # original query params. The pagination loop must not re-pass `params`,
        # or requests appends them a second time and they accumulate page over
        # page until VAN 404s. Regression test for that bug.
        base = self.van.connection.uri + "events"
        next_link = base + "?startingAfter=2020-01-01&%24top=50&%24skip=50"

        page_one = {
            "count": 2,
            "items": [{"eventId": 1}],
            "nextPageLink": next_link,
        }
        page_two = {
            "count": 2,
            "items": [{"eventId": 2}],
            "nextPageLink": None,
        }

        m.get(base, json=page_one)
        m.get(next_link, json=page_two)

        events = self.van.get_events(starting_after="2020-01-01")

        # Both pages were collected.
        assert events.num_rows == 2

        # The second (paginated) request hit the nextPageLink with each query
        # param appearing exactly once -- nothing re-appended.
        paginated_request = m.request_history[-1]
        assert "$skip" in paginated_request.qs  # we followed the link
        for key, values in paginated_request.qs.items():
            assert len(values) == 1, f"param {key!r} was duplicated: {values}"

    @requests_mock.Mocker()
    def test_get_event(self, m):
        event_id = 1062

        json = {
            "eventId": 1062,
            "startDate": "2010-05-25T11:00:00-05:00",
            "codes": "null",
            "endDate": "2010-05-25T15:00:00-05:00",
            "name": "Sample",
            "roles": "null",
            "isOnlyEditableByCreatingUser": "true",
            "ticketCategories": "null",
            "eventType": {"eventTypeId": 29166, "name": "Confirmation Calls"},
            "notes": "null",
            "districtFieldValue": "null",
            "locations": "null",
            "shifts": "null",
            "voterRegistrationBatches": "null",
            "createdDate": "2010-05-25T11:55:00Z",
            "financialProgram": "null",
            "shortName": "Sample",
            "isPubliclyViewable": "null",
            "isActive": "true",
            "description": "This is a sample",
        }

        m.get(self.van.connection.uri + f"events/{event_id}", json=json)

        assert json == self.van.get_event(event_id)

    @requests_mock.Mocker()
    def test_create_event(self, m):
        m.post(self.van.connection.uri + "events", json=750000984, status_code=204)

        # Test that it doesn't throw and error
        r = self.van.create_event(
            "Canvass 01",
            "Can01",
            "2016-06-01",
            "2016-06-02",
            296199,
            [259236],
            publicly_viewable="True",
            editable=False,
        )

        assert r == 750000984

    @requests_mock.Mocker()
    def test_get_event_types(self, m):
        json = [
            {
                "eventTypeId": 296199,
                "name": "Block Party",
                "canHaveMultipleShifts": False,
                "canHaveMultipleLocations": False,
                "canHaveGoals": False,
                "canHaveRoleMaximums": False,
                "canHaveRoleMinimums": False,
                "canBeRepeatable": False,
                "roles": [
                    {"roleId": 259236, "name": "Attendee", "isEventLead": False},
                    {"roleId": 259235, "name": "Supporter", "isEventLead": False},
                    {"roleId": 259234, "name": "Volunteer", "isEventLead": False},
                ],
                "statuses": [
                    {"statusId": 4, "name": "Invited"},
                    {"statusId": 18, "name": "Left Msg"},
                    {"statusId": 14, "name": "Tentative"},
                    {"statusId": 3, "name": "Declined"},
                    {"statusId": 11, "name": "Confirmed"},
                    {"statusId": 23, "name": "Conf Twice"},
                    {"statusId": 2, "name": "Completed"},
                    {"statusId": 15, "name": "Walk In"},
                    {"statusId": 6, "name": "No Show"},
                    {"statusId": 29, "name": "Texted"},
                ],
                "color": "#7F7F7F",
                "isAtLeastOneLocationRequired": False,
                "defaultLocation": None,
                "isSharedWithMasterCommitteeByDefault": False,
                "isSharedWithChildCommitteesByDefault": False,
                "isOnlineActionsAvailable": False,
            }
        ]

        m.get(self.van.connection.uri + "events/types", json=json)

        expected = [
            "eventTypeId",
            "name",
            "canHaveMultipleShifts",
            "canHaveMultipleLocations",
            "canHaveGoals",
            "canHaveRoleMaximums",
            "canHaveRoleMinimums",
            "canBeRepeatable",
            "roles",
            "statuses",
            "color",
            "isAtLeastOneLocationRequired",
            "defaultLocation",
            "isSharedWithMasterCommitteeByDefault",
            "isSharedWithChildCommitteesByDefault",
            "isOnlineActionsAvailable",
        ]

        assert validate_list(expected, self.van.get_event_types())
