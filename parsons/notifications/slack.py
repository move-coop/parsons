import os
import time
import warnings

from parsons.etl.table import Table
from parsons.utilities.check_env import check

from slackclient import SlackClient
from slackclient.exceptions import SlackClientError

import requests


class Slack(object):
    def __init__(self, api_key=None):
        if api_key is None:
            try:
                self.api_key = os.environ["SLACK_API_TOKEN"]

            except KeyError:
                raise KeyError(
                    "Missing api_key. It must be passed as an "
                    "argument or stored as environmental variable"
                )

        else:
            self.api_key = api_key

        self.client = SlackClient(self.api_key)

    def channels(self, fields=["id", "name"], exclude_archived=False, types=["public_channel"]):
        """
        Return a list of all channels in a Slack team.

        `Args:`
            fields: list
                A list of the fields to return. By default, only the channel
                `id` and `name` are returned. See
                https://api.slack.com/methods/conversations.list for a full
                list of available fields. `Notes:` nested fields are unpacked.
            exclude_archived: bool
                Set to `True` to exclude archived channels from the list.
                Default is false.
            types: list
                Mix and match channel types by providing a list of any
                combination of `public_channel`, `private_channel`,
                `mpim` (aka group messages), or `im` (aka 1-1 messages).
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        tbl = self._paginate_request(
            "conversations.list",
            "channels",
            types=types,
            exclude_archived=exclude_archived,
        )

        tbl.unpack_dict("topic", include_original=False, prepend=True, prepend_value="topic")
        tbl.unpack_dict("purpose", include_original=False, prepend=True, prepend_value="purpose")

        rm_cols = [x for x in tbl.columns if x not in fields]
        tbl.remove_column(*rm_cols)

        return tbl

    def users(
        self,
        fields=[
            "id",
            "name",
            "deleted",
            "profile_real_name_normalized",
            "profile_email",
        ],
    ):
        """
        Return a list of all users in a Slack team.

        `Args:`
            fields: list
                A list of the fields to return. By default, only the user
                `id` and `name` and `deleted` status are returned. See
                https://api.slack.com/methods/users.list for a full list of
                available fields. `Notes:` nested fields are unpacked.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self._paginate_request("users.list", "members", include_locale=True)

        tbl.unpack_dict("profile", include_original=False, prepend=True, prepend_value="profile")

        rm_cols = [x for x in tbl.columns if x not in fields]
        tbl.remove_column(*rm_cols)

        return tbl

    @classmethod
    def message(cls, channel, text, webhook=None, parent_message_id=None):
        """
        Send a message to a Slack channel with a webhook instead of an api_key.
        You might not have the full-access API key but still want to notify a channel
        `Args:`
            channel: str
                The name or id of a `public_channel`, a `private_channel`, or
                an `im` (aka 1-1 message).
            text: str
                Text of the message to send.
            webhook: str
                If you have a webhook url instead of an api_key
                Looks like: https://hooks.slack.com/services/Txxxxxxx/Bxxxxxx/Dxxxxxxx
            parent_message_id: str
                The `ts` value of the parent message. If used, this will thread the message.
        """
        webhook = check("SLACK_API_WEBHOOK", webhook, optional=True)
        payload = {"channel": channel, "text": text}
        if parent_message_id:
            payload["thread_ts"] = parent_message_id
        return requests.post(webhook, json=payload)

    def message_channel(self, channel, text, parent_message_id=None, **kwargs):
        """
        Send a message to a Slack channel

        `Args:`
            channel: str
                The name or id of a `public_channel`, a `private_channel`, or
                an `im` (aka 1-1 message).
            text: str
                Text of the message to send.
            parent_message_id: str
                The `ts` value of the parent message. If used, this will thread the message.
            **kwargs: kwargs
                as_user: str
                    This is a deprecated argument. Use optional username, icon_url, and icon_emoji
                    args to customize the attributes of the user posting the message.
                    See https://api.slack.com/methods/chat.postMessage#legacy_authorship for
                    more information about legacy authorship
                Additional arguments for chat.postMessage API call. See documentation
                <https://api.slack.com/methods/chat.postMessage>` for more info.


        `Returns:`
            `dict`:
                A response json
        """

        if "as_user" in kwargs:
            warnings.warn(
                "as_user is a deprecated argument on message_channel().",
                DeprecationWarning,
                stacklevel=2,
            )
        if "thread_ts" in kwargs:
            warnings.warn(
                "thread_ts argument on message_channel() will be ignored. Use parent_message_id.",
                Warning,
                stacklevel=2,
            )
            kwargs.pop("thread_ts", None)

        resp = self.client.api_call(
            "chat.postMessage",
            channel=channel,
            text=text,
            thread_ts=parent_message_id,
            **kwargs,
        )

        if not resp["ok"]:
            if resp["error"] == "ratelimited":
                time.sleep(int(resp["headers"]["Retry-After"]))

                resp = self.client.api_call(
                    "chat.postMessage", channel=channel, text=text, **kwargs
                )

            resp.pop("headers", None)

            raise SlackClientError(resp)

        return resp

    def upload_file(
        self,
        channels,
        filename,
        filetype=None,
        initial_comment=None,
        title=None,
        is_binary=False,
    ):
        """
        Upload a file to Slack channel(s).

        `Args:`
            channels: list
                The list of channel names or IDs where the file will be shared.
            filename: str
                The path to the file to be uploaded.
            filetype: str
                A file type identifier. If None, type will be inferred base on
                file extension. This is used to determine what fields are
                available for that object. See https://api.slack.com/types/file
                for a list of valid types and for more information about the
                file object.
            initial_comment: str
                The text of the message to send along with the file.
            title: str
                Title of the file to be uploaded.
            is_binary: bool
                If True, open this file in binary mode. This is needed if
                uploading binary files. Defaults to False.
        `Returns:`
            `dict`:
                A response json
        """
        if filetype is None and "." in filename:
            filetype = filename.split(".")[-1]

        mode = "rb" if is_binary else "r"
        with open(filename, mode) as file_content:
            resp = self.client.api_call(
                "files.upload",
                channels=channels,
                file=file_content,
                filetype=filetype,
                initial_comment=initial_comment,
                title=title,
            )

            if not resp["ok"]:
                if resp["error"] == "ratelimited":
                    time.sleep(int(resp["headers"]["Retry-After"]))

                    resp = self.client.api_call(
                        "files.upload",
                        channels=channels,
                        file=file_content,
                        filetype=filetype,
                        initial_comment=initial_comment,
                        title=title,
                    )

                raise SlackClientError(resp["error"])

        return resp

    def _paginate_request(self, endpoint, collection, **kwargs):
        # The max object we're requesting at a time.
        # This is an nternal limit to not overload slack api
        LIMIT = 200

        items = []
        next_page = True
        cursor = None
        while next_page:
            resp = self.client.api_call(endpoint, cursor=cursor, limit=LIMIT, **kwargs)

            if not resp["ok"]:
                if resp["error"] == "ratelimited":
                    time.sleep(int(resp["headers"]["Retry-After"]))
                    continue

                raise SlackClientError(resp["error"])

            items.extend(resp[collection])

            if resp["response_metadata"]["next_cursor"]:
                cursor = resp["response_metadata"]["next_cursor"]
            else:
                next_page = False

        return Table(items)
