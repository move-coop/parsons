import unittest
import os
import requests_mock
from parsons import VAN, Table


def assert_matching_tables(table1, table2, ignore_headers=False):
    if ignore_headers:
        data1 = table1.data
        data2 = table2.data
    else:
        data1 = table1
        data2 = table2

    if isinstance(data1, Table) and isinstance(data2, Table):
        assert data1.num_rows == data2.num_rows

    for r1, r2 in zip(data1, data2):
        # Cast both rows to lists, in case they are different types of collections. Must call
        # .items() on dicts to compare content of collections
        if isinstance(r1, dict):
            r1 = r1.items()
        if isinstance(r2, dict):
            r2 = r2.items()

        assert list(r1) == list(r2)


os.environ["VAN_API_KEY"] = "SOME_KEY"

mock_response = [
    {
        "foreignMessageId": "oK2ahdAcEe6F-QAiSCI3lA2",
        "name": "Test Email",
        "createdBy": "Joe Biden",
        "dateCreated": "2024-02-20T13:20:00Z",
        "dateScheduled": "2024-02-20T15:55:00Z",
        "campaignID": 0,
        "dateModified": "2024-02-20T15:54:36.27Z",
        "emailMessageContent": None,
    },
    {
        "foreignMessageId": "rjzc2szzEe6F-QAiSCI3lA2",
        "name": "Test Email 2",
        "createdBy": "Joe Biden",
        "dateCreated": "2024-02-16T12:49:00Z",
        "dateScheduled": "2024-02-16T13:29:00Z",
        "campaignID": 0,
        "dateModified": "2024-02-16T13:29:16.453Z",
        "emailMessageContent": None,
    },
    {
        "foreignMessageId": "_E1AfcnkEe6F-QAiSCI3lA2",
        "name": "Test Email 3",
        "createdBy": "Joe Biden",
        "dateCreated": "2024-02-12T15:26:00Z",
        "dateScheduled": "2024-02-13T11:22:00Z",
        "campaignID": 0,
        "dateModified": "2024-02-13T11:22:28.273Z",
        "emailMessageContent": None,
    },
    {
        "foreignMessageId": "6GTLBsUwEe62YAAiSCIxlw2",
        "name": "Test Email 4",
        "createdBy": "Joe Biden",
        "dateCreated": "2024-02-06T15:47:00Z",
        "dateScheduled": "2024-02-07T10:32:00Z",
        "campaignID": 0,
        "dateModified": "2024-02-07T10:31:55.16Z",
        "emailMessageContent": None,
    },
    {
        "foreignMessageId": "mgTdmcEiEe62YAAiSCIxlw2",
        "name": "Test Email 5",
        "createdBy": "Joe Biden",
        "dateCreated": "2024-02-01T11:55:00Z",
        "dateScheduled": "2024-02-01T16:08:00Z",
        "campaignID": 0,
        "dateModified": "2024-02-01T16:08:10.737Z",
        "emailMessageContent": None,
    },
]


class TestEmail(unittest.TestCase):
    def setUp(self):
        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters", raise_for_status=False)

    @requests_mock.Mocker()
    def test_get_email_messages(self, m):
        m.get(
            self.van.connection.uri + "email/messages",
            json=mock_response,
            status_code=200,
        )

        response = self.van.get_emails()

        assert_matching_tables(response, mock_response)

    @requests_mock.Mocker()
    def test_get_email_message(self, m):
        m.get(
            self.van.connection.uri + "email/message/1",
            json=mock_response[0],
            status_code=200,
        )

        response = self.van.get_email(1)

        assert_matching_tables(response, mock_response[0])
