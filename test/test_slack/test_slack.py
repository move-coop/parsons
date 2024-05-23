from parsons import Table, Slack

from slackclient.exceptions import SlackClientError

import os
import requests_mock
import unittest
import json


_dir = os.path.dirname(__file__)
responses_dir = f"{_dir}/responses"


class TestSlack(unittest.TestCase):
    def setUp(self):
        os.environ["SLACK_API_TOKEN"] = "SOME_API_TOKEN"

        self.slack = Slack()

    def tearDown(self):

        pass

    def test_slack_init(self):
        # Delete to test that is raises an error
        del os.environ["SLACK_API_TOKEN"]

        self.assertNotIn("SLACK_API_TOKEN", os.environ)

        self.assertRaises(KeyError, Slack)

        os.environ["SLACK_API_TOKEN"] = "SOME_API_TOKEN"
        self.assertIn("SLACK_API_TOKEN", os.environ)

    @requests_mock.Mocker()
    def test_channels(self, m):

        with open(f"{responses_dir}/channels.json", "r") as f:
            slack_resp = json.load(f)

        m.post("https://slack.com/api/conversations.list", json=slack_resp)

        tbl = self.slack.channels()

        self.assertIsInstance(tbl, Table)

        expected_columns = ["id", "name"]
        self.assertListEqual(tbl.columns, expected_columns)
        self.assertEqual(tbl.num_rows, 2)

    @requests_mock.Mocker()
    def test_channels_all_fields(self, m):

        with open(f"{responses_dir}/channels.json", "r") as f:
            slack_resp = json.load(f)

        m.post("https://slack.com/api/conversations.list", json=slack_resp)

        fields_req = [
            "id",
            "name",
            "is_channel",
            "created",
            "creator",
            "is_archived",
            "is_general",
            "name_normalized",
            "is_shared",
            "is_org_shared",
            "is_member",
            "is_private",
            "is_mpim",
            "members",
            "topic_value",
            "topic_creator",
            "topic_last_set",
            "purpose_value",
            "purpose_creator",
            "purpose_last_set",
            "previous_names",
            "num_members",
        ]
        tbl = self.slack.channels(fields=fields_req)

        self.assertIsInstance(tbl, Table)

        expected_columns = [
            "id",
            "name",
            "is_channel",
            "created",
            "creator",
            "is_archived",
            "is_general",
            "name_normalized",
            "is_shared",
            "is_org_shared",
            "is_member",
            "is_private",
            "is_mpim",
            "members",
            "topic_value",
            "topic_creator",
            "topic_last_set",
            "purpose_value",
            "purpose_creator",
            "purpose_last_set",
            "previous_names",
            "num_members",
        ]

        self.assertListEqual(sorted(tbl.columns), sorted(expected_columns))
        self.assertEqual(tbl.num_rows, 2)

    @requests_mock.Mocker()
    def test_users(self, m):

        with open(f"{responses_dir}/users.json", "r") as f:
            slack_resp = json.load(f)

        m.post("https://slack.com/api/users.list", json=slack_resp)

        tbl = self.slack.users()

        self.assertIsInstance(tbl, Table)

        expected_columns = [
            "id",
            "name",
            "deleted",
            "profile_email",
            "profile_real_name_normalized",
        ]
        self.assertListEqual(tbl.columns, expected_columns)
        self.assertEqual(tbl.num_rows, 2)

    @requests_mock.Mocker()
    def test_users_all_fields(self, m):

        with open(f"{responses_dir}/users.json", "r") as f:
            slack_resp = json.load(f)

        m.post("https://slack.com/api/users.list", json=slack_resp)

        fields_req = [
            "id",
            "team_id",
            "name",
            "deleted",
            "color",
            "real_name",
            "tz",
            "tz_label",
            "tz_offset",
            "is_admin",
            "is_owner",
            "is_primary_owner",
            "is_restricted",
            "is_ultra_restricted",
            "is_bot",
            "updated",
            "is_app_user",
            "has_2fa",
            "profile_avatar_hash",
            "profile_display_name",
            "profile_display_name_normalized",
            "profile_email",
            "profile_first_name",
            "profile_image_1024",
            "profile_image_192",
            "profile_image_24",
            "profile_image_32",
            "profile_image_48",
            "profile_image_512",
            "profile_image_72",
            "profile_image_original",
            "profile_last_name",
            "profile_phone",
            "profile_real_name",
            "profile_real_name_normalized",
            "profile_skype",
            "profile_status_emoji",
            "profile_status_text",
            "profile_team",
            "profile_title",
        ]
        tbl = self.slack.users(fields=fields_req)

        self.assertIsInstance(tbl, Table)

        expected_columns = [
            "id",
            "team_id",
            "name",
            "deleted",
            "color",
            "real_name",
            "tz",
            "tz_label",
            "tz_offset",
            "is_admin",
            "is_owner",
            "is_primary_owner",
            "is_restricted",
            "is_ultra_restricted",
            "is_bot",
            "updated",
            "is_app_user",
            "has_2fa",
            "profile_avatar_hash",
            "profile_display_name",
            "profile_display_name_normalized",
            "profile_email",
            "profile_first_name",
            "profile_image_1024",
            "profile_image_192",
            "profile_image_24",
            "profile_image_32",
            "profile_image_48",
            "profile_image_512",
            "profile_image_72",
            "profile_image_original",
            "profile_last_name",
            "profile_phone",
            "profile_real_name",
            "profile_real_name_normalized",
            "profile_skype",
            "profile_status_emoji",
            "profile_status_text",
            "profile_team",
            "profile_title",
        ]
        self.assertListEqual(sorted(tbl.columns), sorted(expected_columns))
        self.assertEqual(tbl.num_rows, 2)

    @requests_mock.Mocker()
    def test_message_channel(self, m):

        with open(f"{responses_dir}/message_channel.json", "r") as f:
            slack_resp = json.load(f)

        m.post("https://slack.com/api/chat.postMessage", json=slack_resp)

        dct = self.slack.message_channel("C1H9RESGL", "Here's a message for you")

        self.assertIsInstance(dct, dict)
        self.assertListEqual(sorted(dct), sorted(slack_resp))

        m.post(
            "https://slack.com/api/chat.postMessage",
            json={"ok": False, "error": "invalid_auth"},
        )

        self.assertRaises(
            SlackClientError,
            self.slack.message_channel,
            "FakeChannel",
            "Here's a message for you",
        )

    @requests_mock.Mocker(case_sensitive=True)
    def test_message(self, m):
        webhook = "https://hooks.slack.com/services/T1234/B1234/D12322"
        m.post(webhook, json={"ok": True})
        Slack.message("#foobar", "this is a message", webhook)
        self.assertEqual(
            m._adapter.last_request.json(),
            {"text": "this is a message", "channel": "#foobar"},
        )
        self.assertEqual(m._adapter.last_request.path, "/services/T1234/B1234/D12322")

    @requests_mock.Mocker()
    def test_file_upload(self, m):

        file_path = f"{responses_dir}/file_upload.json"
        with open(file_path, "r") as f:
            slack_resp = json.load(f)

        m.post("https://slack.com/api/files.upload", json=slack_resp)

        dct = self.slack.upload_file(["D0L4B9P0Q"], file_path)

        self.assertIsInstance(dct, dict)
        self.assertListEqual(sorted(dct), sorted(slack_resp))

        m.post(
            "https://slack.com/api/files.upload",
            json={"ok": False, "error": "invalid_auth"},
        )

        self.assertRaises(SlackClientError, self.slack.upload_file, ["D0L4B9P0Q"], file_path)
