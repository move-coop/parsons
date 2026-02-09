import json
import os
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

    def test_slack_init_with_api_key(self):
        # Test initialization with api_key parameter
        slack = Slack(api_key="test_token")
        assert slack.api_key == "test_token"

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

    def _setup_message_channel_mocks(self, include_success_response=True):
        """Helper to set up common mocks for message_channel tests."""
        # Mock channels response for _resolve_channel_id
        mock_channels_response = MagicMock()
        mock_channels_response.data = {
            "channels": [{"id": "C1H9RESGL", "name": "test-channel"}],
            "response_metadata": {"next_cursor": ""},
        }
        self.slack.client.conversations_list = MagicMock(return_value=mock_channels_response)

        if include_success_response:
            with (responses_dir / "message_channel.json").open(mode="r") as f:
                slack_resp = json.load(f)

            mock_response = MagicMock()
            mock_response.data = slack_resp
            self.slack.client.chat_postMessage = MagicMock(return_value=mock_response)

            return slack_resp

        return None

    def test_message_channel_success(self):
        slack_resp = self._setup_message_channel_mocks()

        dct = self.slack.message_channel("C1H9RESGL", "Here's a message for you")

        assert isinstance(dct, dict)
        assert sorted(dct) == sorted(slack_resp)

    def test_message_channel_deprecated_kwargs(self):
        self._setup_message_channel_mocks()

        # Test deprecation of as_user kwarg
        with pytest.warns(
            DeprecationWarning,
            match="as_user is a deprecated argument on message_channel()",
        ):
            self.slack.message_channel(
                "C1H9RESGL", "Here's a message for you", as_user="randomvalue"
            )
        # Verify thread_ts was passed to chat_postMessage
        call_kwargs = self.slack.client.chat_postMessage.call_args.kwargs
        assert "as_user" in call_kwargs, "as_user should be passed to chat_postMessage"

        # Test deprecation of thread_ts kwarg
        with pytest.warns(Warning, match="thread_ts argument on message_channel"):
            self.slack.message_channel(
                "C1H9RESGL", "Here's a message for you", thread_ts="randomvalue"
            )

        # Verify thread_ts was NOT passed to chat_postMessage
        call_kwargs = self.slack.client.chat_postMessage.call_args.kwargs
        assert call_kwargs["thread_ts"] is None, (
            "thread_ts should not be passed to chat_postMessage"
        )

    def test_message_channel_error(self):
        self._setup_message_channel_mocks(include_success_response=False)

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
            "response_metadata": {"next_cursor": ""},
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

    def test_resolve_channel_id_with_channel_id(self):
        # Test that channel IDs starting with C, D, or G are returned unchanged
        assert self.slack._resolve_channel_id("C1H9RESGL") == "C1H9RESGL"
        assert self.slack._resolve_channel_id("D0L4B9P0Q") == "D0L4B9P0Q"
        assert self.slack._resolve_channel_id("G12345678") == "G12345678"

    def test_resolve_channel_id_with_channel_name(self):
        # Mock channels response using actual channels.json data
        with (responses_dir / "channels.json").open(mode="r") as f:
            slack_resp = json.load(f)

        mock_channels_response = MagicMock()
        mock_channels_response.data = slack_resp

        self.slack.client.conversations_list = MagicMock(return_value=mock_channels_response)

        # Test resolving channel name "random" -> "C0G9QF9GW"
        channel_id = self.slack._resolve_channel_id("random")
        assert channel_id == "C0G9QF9GW"

        # Test resolving channel name "general" -> "C0G9QKBBL"
        channel_id = self.slack._resolve_channel_id("general")
        assert channel_id == "C0G9QKBBL"

    def test_resolve_channel_id_with_hash_prefix(self):
        # Mock channels response using actual channels.json data
        with (responses_dir / "channels.json").open(mode="r") as f:
            slack_resp = json.load(f)

        mock_channels_response = MagicMock()
        mock_channels_response.data = slack_resp

        self.slack.client.conversations_list = MagicMock(return_value=mock_channels_response)

        # Test resolving channel name with # prefix "#general" -> "C0G9QKBBL"
        channel_id = self.slack._resolve_channel_id("#general")
        assert channel_id == "C0G9QKBBL"

        # Test resolving channel name with # prefix "#random" -> "C0G9QF9GW"
        channel_id = self.slack._resolve_channel_id("#random")
        assert channel_id == "C0G9QF9GW"

    def test_resolve_channel_id_not_found(self):
        # Mock channels response using actual channels.json data
        with (responses_dir / "channels.json").open(mode="r") as f:
            slack_resp = json.load(f)

        mock_channels_response = MagicMock()
        mock_channels_response.data = slack_resp

        self.slack.client.conversations_list = MagicMock(return_value=mock_channels_response)

        # Test that ValueError is raised when channel not found
        with pytest.raises(ValueError, match="Channel 'nonexistent' not found"):
            self.slack._resolve_channel_id("nonexistent")

    def test_paginate_request_with_pagination(self):
        # Mock paginated response
        mock_response_page1 = MagicMock()
        mock_response_page1.data = {
            "channels": [
                {"id": "C1", "name": "channel1"},
                {"id": "C2", "name": "channel2"},
            ],
            "response_metadata": {"next_cursor": "cursor123"},
        }

        mock_response_page2 = MagicMock()
        mock_response_page2.data = {
            "channels": [
                {"id": "C3", "name": "channel3"},
            ],
            "response_metadata": {"next_cursor": ""},
        }

        self.slack.client.conversations_list = MagicMock(
            side_effect=[mock_response_page1, mock_response_page2]
        )

        tbl = self.slack._paginate_request("conversations_list", "channels")

        assert isinstance(tbl, Table)
        assert tbl.num_rows == 3
        assert self.slack.client.conversations_list.call_count == 2

    def test_paginate_request_unsupported_endpoint(self):
        # Test that ValueError is raised for unsupported endpoints
        with pytest.raises(ValueError, match="Unsupported endpoint: invalid_endpoint"):
            self.slack._paginate_request("invalid_endpoint", "data")

    def test_upload_file_single_channel(self):
        file_path = responses_dir / "file_upload.json"
        with file_path.open(mode="r") as f:
            slack_resp = json.load(f)

        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Mock channels response for _resolve_channel_id
        mock_channels_response = MagicMock()
        mock_channels_response.data = {
            "channels": [{"id": "D0L4B9P0Q", "name": "test-channel"}],
            "response_metadata": {"next_cursor": ""},
        }

        self.slack.client.files_upload_v2 = MagicMock(return_value=mock_response)
        self.slack.client.conversations_list = MagicMock(return_value=mock_channels_response)

        # Test with single channel as string
        dct = self.slack.upload_file("D0L4B9P0Q", str(file_path))

        assert isinstance(dct, dict)
        assert sorted(dct) == sorted(slack_resp)
        assert self.slack.client.files_upload_v2.call_count == 1

    def test_upload_file_multiple_channels(self):
        file_path = responses_dir / "file_upload.json"
        with file_path.open(mode="r") as f:
            slack_resp = json.load(f)

        mock_response = MagicMock()
        mock_response.data = slack_resp

        # Mock channels response for _resolve_channel_id
        mock_channels_response = MagicMock()
        mock_channels_response.data = {
            "channels": [
                {"id": "D0L4B9P0Q", "name": "channel1"},
                {"id": "C1H9RESGL", "name": "channel2"},
            ],
            "response_metadata": {"next_cursor": ""},
        }

        self.slack.client.files_upload_v2 = MagicMock(return_value=mock_response)
        self.slack.client.conversations_list = MagicMock(return_value=mock_channels_response)

        # Test with multiple channels as list
        dct = self.slack.upload_file(["D0L4B9P0Q", "C1H9RESGL"], str(file_path))

        assert isinstance(dct, dict)
        assert self.slack.client.files_upload_v2.call_count == 2

    def test_message_channel_with_thread(self):
        with (responses_dir / "message_channel.json").open(mode="r") as f:
            slack_resp = json.load(f)

        mock_response = MagicMock()
        mock_response.data = slack_resp

        mock_channels_response = MagicMock()
        mock_channels_response.data = {
            "channels": [{"id": "C1H9RESGL", "name": "test-channel"}],
            "response_metadata": {"next_cursor": ""},
        }

        self.slack.client.chat_postMessage = MagicMock(return_value=mock_response)
        self.slack.client.conversations_list = MagicMock(return_value=mock_channels_response)

        # Test with parent_message_id for threading
        dct = self.slack.message_channel(
            "C1H9RESGL", "Here's a threaded message", parent_message_id="1234567890.123456"
        )

        assert isinstance(dct, dict)
        # Verify thread_ts was passed
        call_kwargs = self.slack.client.chat_postMessage.call_args[1]
        assert call_kwargs["thread_ts"] == "1234567890.123456"

    def test_channels_with_types(self):
        with (responses_dir / "channels.json").open(mode="r") as f:
            slack_resp = json.load(f)

        mock_response = MagicMock()
        mock_response.data = slack_resp

        self.slack.client.conversations_list = MagicMock(return_value=mock_response)

        _ = self.slack.channels(types=["public_channel", "private_channel"])

        # Verify types were passed correctly
        call_kwargs = self.slack.client.conversations_list.call_args[1]
        assert call_kwargs["types"] == "public_channel,private_channel"
