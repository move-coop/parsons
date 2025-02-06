import unittest
import os
import requests_mock
from copy import deepcopy
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


sample_content_full = [
    {
        "name": "Email Name",
        "senderDisplayName": "Joe Biden",
        "senderEmailAddress": "joe@biden.org",
        "subject": "This is Joe",
        "createdBy": "Random Intern",
        "dateCreated": "2023-05-17T15:04:00Z",
        "emailMessageContentDistributions": {
            "dateSent": "2023-05-17T15:05:00Z",
            "recipientCount": 10,
            "openCount": 0,
            "linksClickedCount": 0,
            "unsubscribeCount": 0,
            "bounceCount": 0,
            "contributionTotal": 0.0,
            "formSubmissionCount": 0,
            "contributionCount": 0,
            "machineOpenCount": 0,
        },
    },
    {
        "name": "Email Name_B",
        "senderDisplayName": "Kamala Harris",
        "senderEmailAddress": "kamala@harris.org",
        "subject": "This is Kamala",
        "createdBy": "Random Intern",
        "dateCreated": "2023-05-17T15:04:00Z",
        "emailMessageContentDistributions": {
            "dateSent": "2023-05-17T15:05:00Z",
            "recipientCount": 10,
            "openCount": 1,
            "linksClickedCount": 1,
            "unsubscribeCount": 1,
            "bounceCount": 0,
            "contributionTotal": 1.0,
            "formSubmissionCount": 0,
            "contributionCount": 1,
            "machineOpenCount": 1,
        },
    },
    {
        "name": "Email Name_C",
        "senderDisplayName": "Commander Biden",
        "senderEmailAddress": "commander@barkbark.org",
        "subject": "Bark Bark",
        "createdBy": "Random Intern",
        "dateCreated": "2023-05-17T15:04:00Z",
        "emailMessageContentDistributions": {
            "dateSent": "2023-05-17T15:05:00Z",
            "recipientCount": 10,
            "openCount": 5,
            "linksClickedCount": 0,
            "unsubscribeCount": 0,
            "bounceCount": 0,
            "contributionTotal": 0.0,
            "formSubmissionCount": 0,
            "contributionCount": 0,
            "machineOpenCount": 2,
        },
    },
    {
        "name": "Email Name_Winner",
        "senderDisplayName": "Commander Biden",
        "senderEmailAddress": "commander@barkbark.org",
        "subject": "Bark Bark",
        "createdBy": "TargetedEmail InternalAPIUser",
        "dateCreated": "2023-05-17T17:06:00Z",
        "emailMessageContentDistributions": {
            "dateSent": "2023-05-17T17:06:00Z",
            "recipientCount": 100,
            "openCount": 30,
            "linksClickedCount": 10,
            "unsubscribeCount": 10,
            "bounceCount": 10,
            "contributionTotal": 500.0,
            "formSubmissionCount": 0,
            "contributionCount": 3,
            "machineOpenCount": 30,
        },
    },
]

sample_content_single = [
    {
        "name": "Email Name",
        "senderDisplayName": "Joe Biden",
        "senderEmailAddress": "joe@biden.org",
        "subject": "This is Joe",
        "createdBy": "Random Intern",
        "dateCreated": "2023-05-17T15:04:00Z",
        "emailMessageContentDistributions": {
            "dateSent": "2023-05-17T15:05:00Z",
            "recipientCount": 10,
            "openCount": 0,
            "linksClickedCount": 0,
            "unsubscribeCount": 0,
            "bounceCount": 0,
            "contributionTotal": 0.0,
            "formSubmissionCount": 0,
            "contributionCount": 0,
            "machineOpenCount": 0,
        },
    }
]

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
        "foreignMessageId": "E1AfcnkEe6F-QAiSCI3lA2",
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

mock_response_enriched = deepcopy(mock_response)
mock_response_enriched[0]["emailMessageContent"] = sample_content_single
mock_response_enriched[1]["emailMessageContent"] = sample_content_single
mock_response_enriched[2]["emailMessageContent"] = sample_content_single
mock_response_enriched[3]["emailMessageContent"] = sample_content_single
mock_response_enriched[4]["emailMessageContent"] = sample_content_full


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
            self.van.connection.uri + "email/message/0",
            json=mock_response[0],
            status_code=200,
        )
        m.get(
            self.van.connection.uri + "email/message/1",
            json=mock_response_enriched[0],
            status_code=200,
        )
        response0 = self.van.get_email(0, expand=False)
        response1 = self.van.get_email(1)

        assert_matching_tables(response0, mock_response[0])
        assert_matching_tables(response1, mock_response_enriched[0])

    @requests_mock.Mocker()
    def test_get_email_message_stats_agg(self, m):
        m.get(
            self.van.connection.uri + "email/messages",
            json=mock_response_enriched,
            status_code=200,
        )
        for resp in mock_response_enriched:
            m.get(
                self.van.connection.uri + f"email/message/{resp['foreignMessageId']}",
                json=resp,
                status_code=200,
            )

        response_t = self.van.get_email_stats(aggregate_ab=True)
        response_f = self.van.get_email_stats(aggregate_ab=False)

        assert len(response_t.to_dicts()) == 5
        assert len(response_f.to_dicts()) == 8

        assert response_t.to_dicts()[4]["recipientCount"] == 130
        assert response_f.to_dicts()[4]["recipientCount"] == 10
