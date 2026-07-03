import json
import os
from pathlib import Path

import pytest
from slack_sdk.errors import SlackApiError

from parsons import Slack, Table

responses_dir = Path(__file__).parent / "responses"


def _setup_message_channel_mocks(slack, mocker, include_success_response=True):
    """Helper to set up common mocks for message_channel tests."""
    # Mock channels response for _resolve_channel_id
    mock_channels_response = mocker.MagicMock()
    mock_channels_response.data = {
        "channels": [{"id": "C1H9RESGL", "name": "test-channel"}],
        "response_metadata": {"next_cursor": ""},
    }
    slack.client.conversations_list = mocker.MagicMock(return_value=mock_channels_response)

    if include_success_response:
        with (responses_dir / "message_channel.json").open(mode="r") as f:
            slack_resp = json.load(f)

        mock_response = mocker.MagicMock()
        mock_response.data = slack_resp
        slack.client.chat_postMessage = mocker.MagicMock(return_value=mock_response)

        return slack_resp

    return None


def test_slack_init(monkeypatch):
    # Delete to test that it raises an error
    monkeypatch.delenv("SLACK_API_TOKEN", raising=False)

    assert "SLACK_API_TOKEN" not in os.environ

    with pytest.raises(KeyError):
        Slack()

    monkeypatch.setenv("SLACK_API_TOKEN", "SOME_API_TOKEN")
    assert "SLACK_API_TOKEN" in os.environ


def test_slack_init_with_api_key():
    # Test initialization with api_key parameter
    slack = Slack(api_key="test_token")
    assert slack.api_key == "test_token"


def test_channels(slack, mocker):
    with (responses_dir / "channels.json").open(mode="r") as f:
        slack_resp = json.load(f)

    # Mock the response object
    mock_response = mocker.MagicMock()
    mock_response.data = slack_resp

    # Mock the client method directly on the instance
    slack.client.conversations_list = mocker.MagicMock(return_value=mock_response)

    tbl = slack.channels()

    assert isinstance(tbl, Table)
    assert tbl.columns == ["id", "name"]
    assert tbl.num_rows == 2


def test_channels_all_fields(slack, mocker):
    with (responses_dir / "channels.json").open(mode="r") as f:
        slack_resp = json.load(f)

    # Mock the response object
    mock_response = mocker.MagicMock()
    mock_response.data = slack_resp

    # Mock the client method directly on the instance
    slack.client.conversations_list = mocker.MagicMock(return_value=mock_response)

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
    tbl = slack.channels(fields=fields_req)

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


def test_users(slack, mocker):
    with (responses_dir / "users.json").open(mode="r") as f:
        slack_resp = json.load(f)

    # Mock the response object
    mock_response = mocker.MagicMock()
    mock_response.data = slack_resp

    # Mock the client method directly on the instance
    slack.client.users_list = mocker.MagicMock(return_value=mock_response)

    tbl = slack.users()

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


def test_users_all_fields(slack, mocker):
    with (responses_dir / "users.json").open(mode="r") as f:
        slack_resp = json.load(f)

    # Mock the response object
    mock_response = mocker.MagicMock()
    mock_response.data = slack_resp

    # Mock the client method directly on the instance
    slack.client.users_list = mocker.MagicMock(return_value=mock_response)

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
    tbl = slack.users(fields=fields_req)

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


def test_message_channel_success(slack, mocker):
    slack_resp = _setup_message_channel_mocks(slack, mocker)

    dct = slack.message_channel("C1H9RESGL", "Here's a message for you")

    assert isinstance(dct, dict)
    assert sorted(dct) == sorted(slack_resp)


def test_message_channel_deprecated_kwargs(slack, mocker):
    _setup_message_channel_mocks(slack, mocker)

    # Test deprecation of as_user kwarg
    with pytest.warns(
        DeprecationWarning, match="as_user is a deprecated argument on message_channel()"
    ):
        slack.message_channel("C1H9RESGL", "Here's a message for you", as_user="randomvalue")
    # Verify thread_ts was passed to chat_postMessage
    call_kwargs = slack.client.chat_postMessage.call_args.kwargs
    assert "as_user" in call_kwargs, "as_user should be passed to chat_postMessage"

    # Test deprecation of thread_ts kwarg
    with pytest.warns(Warning, match="thread_ts argument on message_channel"):
        slack.message_channel("C1H9RESGL", "Here's a message for you", thread_ts="randomvalue")

    # Verify thread_ts was NOT passed to chat_postMessage
    call_kwargs = slack.client.chat_postMessage.call_args.kwargs
    assert call_kwargs["thread_ts"] is None, "thread_ts should not be passed to chat_postMessage"


def test_message_channel_error(slack, mocker):
    _setup_message_channel_mocks(slack, mocker, include_success_response=False)

    # Test error case
    error_response = mocker.MagicMock()
    error_response.data = {"ok": False, "error": "invalid_auth"}
    slack.client.chat_postMessage = mocker.MagicMock(
        side_effect=SlackApiError("invalid_auth", error_response)
    )

    with pytest.raises(SlackApiError):
        slack.message_channel("C1H9RESGL", "Here's a message for you")


def test_message(requests_mock):
    webhook = "https://hooks.slack.com/services/T1234/B1234/D12322"
    requests_mock.post(webhook, json={"ok": True})
    Slack.message("#foobar", "this is a message", webhook)
    assert requests_mock.last_request.json() == {
        "text": "this is a message",
        "channel": "#foobar",
    }
    # The requests_mock pytest fixture normalizes request paths to lowercase
    # (the standalone Mocker(case_sensitive=True) did not), so compare case-insensitively.
    assert requests_mock.last_request.path == "/services/T1234/B1234/D12322".lower()


def test_file_upload(slack, mocker):
    file_path = responses_dir / "file_upload.json"
    with file_path.open(mode="r") as f:
        slack_resp = json.load(f)

    # Mock the response object
    mock_response = mocker.MagicMock()
    mock_response.data = slack_resp

    # Mock channels response for _resolve_channel_id
    mock_channels_response = mocker.MagicMock()
    mock_channels_response.data = {
        "channels": [{"id": "D0L4B9P0Q", "name": "test-channel"}],
        "response_metadata": {"next_cursor": ""},
    }

    # Mock the client methods directly on the instance
    slack.client.files_upload_v2 = mocker.MagicMock(return_value=mock_response)
    slack.client.conversations_list = mocker.MagicMock(return_value=mock_channels_response)

    dct = slack.upload_file(["D0L4B9P0Q"], str(file_path))

    assert isinstance(dct, dict)
    assert sorted(dct) == sorted(slack_resp)

    # Test error case
    error_response = mocker.MagicMock()
    error_response.data = {"ok": False, "error": "invalid_auth"}
    slack.client.files_upload_v2 = mocker.MagicMock(
        side_effect=SlackApiError("invalid_auth", error_response)
    )

    with pytest.raises(SlackApiError):
        slack.upload_file(["D0L4B9P0Q"], str(file_path))


def test_resolve_channel_id_with_channel_id(slack):
    # Test that channel IDs starting with C, D, or G are returned unchanged
    assert slack._resolve_channel_id("C1H9RESGL") == "C1H9RESGL"
    assert slack._resolve_channel_id("D0L4B9P0Q") == "D0L4B9P0Q"
    assert slack._resolve_channel_id("G12345678") == "G12345678"


def test_resolve_channel_id_with_channel_name(slack, mocker):
    # Mock channels response using actual channels.json data
    with (responses_dir / "channels.json").open(mode="r") as f:
        slack_resp = json.load(f)

    mock_channels_response = mocker.MagicMock()
    mock_channels_response.data = slack_resp

    slack.client.conversations_list = mocker.MagicMock(return_value=mock_channels_response)

    # Test resolving channel name "random" -> "C0G9QF9GW"
    channel_id = slack._resolve_channel_id("random")
    assert channel_id == "C0G9QF9GW"

    # Test resolving channel name "general" -> "C0G9QKBBL"
    channel_id = slack._resolve_channel_id("general")
    assert channel_id == "C0G9QKBBL"


def test_resolve_channel_id_with_hash_prefix(slack, mocker):
    # Mock channels response using actual channels.json data
    with (responses_dir / "channels.json").open(mode="r") as f:
        slack_resp = json.load(f)

    mock_channels_response = mocker.MagicMock()
    mock_channels_response.data = slack_resp

    slack.client.conversations_list = mocker.MagicMock(return_value=mock_channels_response)

    # Test resolving channel name with # prefix "#general" -> "C0G9QKBBL"
    channel_id = slack._resolve_channel_id("#general")
    assert channel_id == "C0G9QKBBL"

    # Test resolving channel name with # prefix "#random" -> "C0G9QF9GW"
    channel_id = slack._resolve_channel_id("#random")
    assert channel_id == "C0G9QF9GW"


def test_resolve_channel_id_not_found(slack, mocker):
    # Mock channels response using actual channels.json data
    with (responses_dir / "channels.json").open(mode="r") as f:
        slack_resp = json.load(f)

    mock_channels_response = mocker.MagicMock()
    mock_channels_response.data = slack_resp

    slack.client.conversations_list = mocker.MagicMock(return_value=mock_channels_response)

    # Test that ValueError is raised when channel not found
    with pytest.raises(ValueError, match="Channel 'nonexistent' not found"):
        slack._resolve_channel_id("nonexistent")


def test_paginate_request_with_pagination(slack, mocker):
    # Mock paginated response
    mock_response_page1 = mocker.MagicMock()
    mock_response_page1.data = {
        "channels": [
            {"id": "C1", "name": "channel1"},
            {"id": "C2", "name": "channel2"},
        ],
        "response_metadata": {"next_cursor": "cursor123"},
    }

    mock_response_page2 = mocker.MagicMock()
    mock_response_page2.data = {
        "channels": [
            {"id": "C3", "name": "channel3"},
        ],
        "response_metadata": {"next_cursor": ""},
    }

    slack.client.conversations_list = mocker.MagicMock(
        side_effect=[mock_response_page1, mock_response_page2]
    )

    tbl = slack._paginate_request("conversations_list", "channels")

    assert isinstance(tbl, Table)
    assert tbl.num_rows == 3
    assert slack.client.conversations_list.call_count == 2


def test_paginate_request_unsupported_endpoint(slack):
    # Test that ValueError is raised for unsupported endpoints
    with pytest.raises(ValueError, match="Unsupported endpoint: invalid_endpoint"):
        slack._paginate_request("invalid_endpoint", "data")


def test_upload_file_single_channel(slack, mocker):
    file_path = responses_dir / "file_upload.json"
    with file_path.open(mode="r") as f:
        slack_resp = json.load(f)

    mock_response = mocker.MagicMock()
    mock_response.data = slack_resp

    # Mock channels response for _resolve_channel_id
    mock_channels_response = mocker.MagicMock()
    mock_channels_response.data = {
        "channels": [{"id": "D0L4B9P0Q", "name": "test-channel"}],
        "response_metadata": {"next_cursor": ""},
    }

    slack.client.files_upload_v2 = mocker.MagicMock(return_value=mock_response)
    slack.client.conversations_list = mocker.MagicMock(return_value=mock_channels_response)

    # Test with single channel as string
    dct = slack.upload_file("D0L4B9P0Q", str(file_path))

    assert isinstance(dct, dict)
    assert sorted(dct) == sorted(slack_resp)
    assert slack.client.files_upload_v2.call_count == 1


def test_upload_file_multiple_channels(slack, mocker):
    file_path = responses_dir / "file_upload.json"
    with file_path.open(mode="r") as f:
        slack_resp = json.load(f)

    mock_response = mocker.MagicMock()
    mock_response.data = slack_resp

    # Mock channels response for _resolve_channel_id
    mock_channels_response = mocker.MagicMock()
    mock_channels_response.data = {
        "channels": [
            {"id": "D0L4B9P0Q", "name": "channel1"},
            {"id": "C1H9RESGL", "name": "channel2"},
        ],
        "response_metadata": {"next_cursor": ""},
    }

    slack.client.files_upload_v2 = mocker.MagicMock(return_value=mock_response)
    slack.client.conversations_list = mocker.MagicMock(return_value=mock_channels_response)

    # Test with multiple channels as list
    dct = slack.upload_file(["D0L4B9P0Q", "C1H9RESGL"], str(file_path))

    assert isinstance(dct, dict)
    assert slack.client.files_upload_v2.call_count == 2


def test_message_channel_with_thread(slack, mocker):
    with (responses_dir / "message_channel.json").open(mode="r") as f:
        slack_resp = json.load(f)

    mock_response = mocker.MagicMock()
    mock_response.data = slack_resp

    mock_channels_response = mocker.MagicMock()
    mock_channels_response.data = {
        "channels": [{"id": "C1H9RESGL", "name": "test-channel"}],
        "response_metadata": {"next_cursor": ""},
    }

    slack.client.chat_postMessage = mocker.MagicMock(return_value=mock_response)
    slack.client.conversations_list = mocker.MagicMock(return_value=mock_channels_response)

    # Test with parent_message_id for threading
    dct = slack.message_channel(
        "C1H9RESGL", "Here's a threaded message", parent_message_id="1234567890.123456"
    )

    assert isinstance(dct, dict)
    # Verify thread_ts was passed
    call_kwargs = slack.client.chat_postMessage.call_args[1]
    assert call_kwargs["thread_ts"] == "1234567890.123456"


def test_channels_with_types(slack, mocker):
    with (responses_dir / "channels.json").open(mode="r") as f:
        slack_resp = json.load(f)

    mock_response = mocker.MagicMock()
    mock_response.data = slack_resp

    slack.client.conversations_list = mocker.MagicMock(return_value=mock_response)

    _ = slack.channels(types=["public_channel", "private_channel"])

    # Verify types were passed correctly
    call_kwargs = slack.client.conversations_list.call_args[1]
    assert call_kwargs["types"] == "public_channel,private_channel"
