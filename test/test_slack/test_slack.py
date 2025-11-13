import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests_mock
from slack_sdk.errors import SlackApiError

from parsons import Slack, Table

responses_dir = Path(__file__).parent / "responses"


class TestSlack(unittest.TestCase):
    def setUp(self):
        self.slack = Slack("SOME_API_TOKEN")

    def tearDown(self):
        pass

    def test_channels(self):
        with (responses_dir / "channels.json").open(mode="r") as f:
            slack_resp = json.load(f)

        # Mock the response object
        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Mock the client method directly on the instance
        self.slack.client.conversations_list = MagicMock(return_value=mock_response)

        tbl = self.slack.channels()

        assert isinstance(tbl, Table)
        assert tbl.columns == ["id", "name"]
        assert tbl.num_rows == 2

    def test_channels_all_fields(self):
        with (responses_dir / "channels.json").open(mode="r") as f:
            slack_resp = json.load(f)

        # Mock the response object
        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Mock the client method directly on the instance
        self.slack.client.conversations_list = MagicMock(return_value=mock_response)

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

    def test_users(self):
        with (responses_dir / "users.json").open(mode="r") as f:
            slack_resp = json.load(f)

        # Mock the response object
        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Mock the client method directly on the instance
        self.slack.client.users_list = MagicMock(return_value=mock_response)

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

    def test_users_all_fields(self):
        with (responses_dir / "users.json").open(mode="r") as f:
            slack_resp = json.load(f)

        # Mock the response object
        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Mock the client method directly on the instance
        self.slack.client.users_list = MagicMock(return_value=mock_response)

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

    def test_message_channel(self):
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

        # Mock the client methods directly on the instance
        self.slack.client.chat_postMessage = MagicMock(return_value=mock_response)
        self.slack.client.conversations_list = MagicMock(return_value=mock_channels_response)

        dct = self.slack.message_channel("C1H9RESGL", "Here's a message for you")

        assert isinstance(dct, dict)
        assert sorted(dct) == sorted(slack_resp)

        # Test error case
        error_response = MagicMock()
        error_response.data = {"ok": False, "error": "invalid_auth"}
        self.slack.client.chat_postMessage = MagicMock(
            side_effect=SlackApiError("invalid_auth", error_response)
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

    def test_file_upload(self):
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

        # Mock the client methods directly on the instance
        self.slack.client.files_upload_v2 = MagicMock(return_value=mock_response)
        self.slack.client.conversations_list = MagicMock(return_value=mock_channels_response)

        dct = self.slack.upload_file(["D0L4B9P0Q"], str(file_path))

        assert isinstance(dct, dict)
        assert sorted(dct) == sorted(slack_resp)

        # Test error case
        error_response = MagicMock()
        error_response.data = {"ok": False, "error": "invalid_auth"}
        self.slack.client.files_upload_v2 = MagicMock(
            side_effect=SlackApiError("invalid_auth", error_response)
        )

        with pytest.raises(SlackApiError):
            self.slack.upload_file(["D0L4B9P0Q"], str(file_path))
