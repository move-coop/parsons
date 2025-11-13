import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests_mock
from slack_sdk.errors import SlackApiError

from parsons import Slack, Table

responses_dir = Path(__file__).parent / "responses"


class TestSlack(unittest.TestCase):
    def setUp(self):
        os.environ["SLACK_API_TOKEN"] = "SOME_API_TOKEN"
        self.slack = Slack()

    def tearDown(self):
        pass

    def test_slack_init(self):
        # Delete to test that it raises an error
        del os.environ["SLACK_API_TOKEN"]

        assert "SLACK_API_TOKEN" not in os.environ

        with pytest.raises(KeyError):
            Slack()

        os.environ["SLACK_API_TOKEN"] = "SOME_API_TOKEN"
        assert "SLACK_API_TOKEN" in os.environ

    @patch('parsons.notifications.slack.WebClient')
    def test_channels(self, mock_webclient):
        with (responses_dir / "channels.json").open(mode="r") as f:
            slack_resp = json.load(f)

        # Mock the response object
        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Configure the mock client
        mock_client_instance = mock_webclient.return_value
        mock_client_instance.conversations_list.return_value = mock_response

        tbl = self.slack.channels()

        assert isinstance(tbl, Table)
        assert tbl.columns == ["id", "name"]
        assert tbl.num_rows == 2

    @patch('parsons.notifications.slack.WebClient')
    def test_channels_all_fields(self, mock_webclient):
        with (responses_dir / "channels.json").open(mode="r") as f:
            slack_resp = json.load(f)

        # Mock the response object
        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Configure the mock client
        mock_client_instance = mock_webclient.return_value
        mock_client_instance.conversations_list.return_value = mock_response

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

        assert isinstance(tbl, Table)

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

        assert sorted(tbl.columns) == sorted(expected_columns)
        assert tbl.num_rows == 2

    @patch('parsons.notifications.slack.WebClient')
    def test_users(self, mock_webclient):
        with (responses_dir / "users.json").open(mode="r") as f:
            slack_resp = json.load(f)

        # Mock the response object
        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Configure the mock client
        mock_client_instance = mock_webclient.return_value
        mock_client_instance.users_list.return_value = mock_response

        tbl = self.slack.users()

        assert isinstance(tbl, Table)

        expected_columns = [
            "id",
            "name",
            "deleted",
            "profile_email",
            "profile_real_name_normalized",
        ]
        assert tbl.columns == expected_columns
        assert tbl.num_rows == 2

    @patch('parsons.notifications.slack.WebClient')
    def test_users_all_fields(self, mock_webclient):
        with (responses_dir / "users.json").open(mode="r") as f:
            slack_resp = json.load(f)

        # Mock the response object
        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Configure the mock client
        mock_client_instance = mock_webclient.return_value
        mock_client_instance.users_list.return_value = mock_response

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

        assert isinstance(tbl, Table)

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
        assert sorted(tbl.columns) == sorted(expected_columns)
        assert tbl.num_rows == 2

    @patch('parsons.notifications.slack.WebClient')
    def test_message_channel(self, mock_webclient):
        with (responses_dir / "message_channel.json").open(mode="r") as f:
            slack_resp = json.load(f)

        # Mock the response object
        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Mock channels response for _resolve_channel_id
        mock_channels_response = MagicMock()
        mock_channels_response.data = {
            "channels": [{"id": "C1H9RESGL", "name": "test-channel"}],
            "response_metadata": {"next_cursor": ""}
        }

        # Configure the mock client
        mock_client_instance = mock_webclient.return_value
        mock_client_instance.chat_postMessage.return_value = mock_response
        mock_client_instance.conversations_list.return_value = mock_channels_response

        dct = self.slack.message_channel("C1H9RESGL", "Here's a message for you")

        assert isinstance(dct, dict)
        assert sorted(dct) == sorted(slack_resp)

        # Test error case
        error_response = MagicMock()
        error_response.data = {"ok": False, "error": "invalid_auth"}
        mock_client_instance.chat_postMessage.side_effect = SlackApiError(
            "invalid_auth", error_response
        )

        with pytest.raises(SlackApiError):
            self.slack.message_channel("C1H9RESGL", "Here's a message for you")

    @requests_mock.Mocker(case_sensitive=True)
    def test_message(self, m):
        webhook = "https://hooks.slack.com/services/T1234/B1234/D12322"
        m.post(webhook, json={"ok": True})
        Slack.message("#foobar", "this is a message", webhook)
        assert m._adapter.last_request.json() == {"text": "this is a message", "channel": "#foobar"}
        assert m._adapter.last_request.path == "/services/T1234/B1234/D12322"

    @patch('parsons.notifications.slack.WebClient')
    def test_file_upload(self, mock_webclient):
        file_path = responses_dir / "file_upload.json"
        with file_path.open(mode="r") as f:
            slack_resp = json.load(f)

        # Mock the response object
        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Mock channels response for _resolve_channel_id
        mock_channels_response = MagicMock()
        mock_channels_response.data = {
            "channels": [{"id": "D0L4B9P0Q", "name": "test-channel"}],
            "response_metadata": {"next_cursor": ""}
        }

        # Configure the mock client
        mock_client_instance = mock_webclient.return_value
        mock_client_instance.files_upload_v2.return_value = mock_response
        mock_client_instance.conversations_list.return_value = mock_channels_response

        dct = self.slack.upload_file(["D0L4B9P0Q"], str(file_path))

        assert isinstance(dct, dict)
        assert sorted(dct) == sorted(slack_resp)

        # Test error case
        error_response = MagicMock()
        error_response.data = {"ok": False, "error": "invalid_auth"}
        mock_client_instance.files_upload_v2.side_effect = SlackApiError(
            "invalid_auth", error_response
        )

        with pytest.raises(SlackApiError):
            self.slack.upload_file(["D0L4B9P0Q"], str(file_path))
