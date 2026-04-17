#####
Slack
#####

Overview
========

The Slack module leverages the Slack API and provides way to easily send
notifications through Slack. It is recommended that you reference the
`Slack API documentation <https://api.slack.com/>`__ for additional details and
information.

.. admonition:: API Tokens

   - Slack API Tokens are required to use this module. To obtain an API
     Token, `create a Slack App <https://api.slack.com/apps>`__ associated
     with the desired Slack workspace. Once you create the app, navigate
     to 'OAuth & Permissions' and add the following OAuth scopes:

     `channels:read`, `users:read`, `chat:write`, and `files:write`

     You can now install the Slack App, which will produce an API Token.
     Note that you can change the scopes any time, but you must reinstall
     the app each time (your API Token will stay the same).

   - Slack has rate limits on all its endpoints.

Quickstart
==========

To call the Slack class you can either store the API Token as an environment
variable `SLACK_API_TOKEN` or pass it in as an argument.

.. code-block:: python
   :caption: Initiate class via environment variable api token

   from parsons import Slack
   slack = Slack()

.. code-block:: python
   :caption: Pass api token directly

   from parsons import Slack
   slack = Slack(api_key='my-api-tkn')

You can then send messages:

.. code-block:: python
   :caption: Send a simple messsage

   slack.message_channel("my_channel", "Hello from python script")

.. code-block:: python
   :caption: Share a file

   slack.upload_file(["channel_1", "channel_2"], "my_slack_file.txt")

API
====

.. autoclass:: parsons.notifications.slack.Slack
   :inherited-members:
   :members:
