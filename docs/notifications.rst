Notifications
=============


==========
Slack
==========


********
Overview
********

The Slack module leverages the Slack API and provides way to easily send
notifications through Slack. It is recommended that you reference the
`Slack API documentation <https://api.slack.com/>`_ for additional details and
information.

.. note::

   API Tokens
      - Slack API Tokens are required to use this module. To obtain an API
        Token, `create a Slack App <https://api.slack.com/apps>`_ associated
        with the desired Slack workspace. Once you create the app, navigate
        to 'OAuth & Permissions' and add the following OAuth scopes:

        `channels:read`, `users:read`, `chat:write`, and `files:write`

        You can now install the Slack App, which will produce an API Token.
        Note that you can change the scopes any time, but you must reinstall
        the app each time (your API Token will stay the same).
      - Slack has rate limits on all its endpoints.

.. toctree::
    :maxdepth: 1

**********
QuickStart
**********

To call the Slack class you can either store the API Token as an environment
variable `SLACK_API_TOKEN` or pass it in as an argument.

.. code-block:: python

  from parsons import Slack

  slack = Slack() # Initiate class via environment variable api token

  slack = Slack(api_key='my-api-tkn') # Pass api token directly

You can then send messages:

.. code-block:: python

  from parsons import Slack

  slack = Slack()

  # send a simple messsage
  slack.message_channel("my_channel", "Hello from python script")

  # share a file
  slack.upload_file(["channel_1", "channel_2"], "my_slack_file.txt")

***
API
***

.. autoclass:: parsons.notifications.slack.Slack
   :inherited-members:
   :members:

==========
Gmail
==========


********
Overview
********

The Gmail module leverages the Gmail API and provides an way to easily send
notifications through email. It is recommended that you reference the
`Gmail API documentation <https://developers.google.com/gmail/api/>`_ for
additional details and information.

.. note::

  Credentials and token
     - Credentials are required to use the class
     - You will need to pass in the path to the credentials and to where a
       generated token will be saved. Typically you’ll get the credentials from
       the Google Developer Console (look for the “Gmail API”).

.. note::

  6MB Attachment Size Limit
     - Currently there is a limit of 6MB when sending attachments.

.. toctree::
    :maxdepth: 1

**********
QuickStart
**********

To call the Gmail class you will need to pass in the path to a
`credentials.json` and the path to `tokens.json`.

.. code-block:: python

 from parsons import Gmail

 gmail = Gmail(
    creds_path="~/secret_location/credentials.json",
    token_path="~/secret_location/token.json")

The easiest way to send a message:

.. code-block:: python

  gmail.send_email(
    "sender@email.com",
    "recipient@email.com",
    "The Subject",
    "This is the text body of the email")

The current version also supports sending html emails and emails with
attachments.

.. code-block:: python

  gmail.send_email(
    "sender@email.com",
    "recipient@email.com",
    "An html email with attachments",
    "This is the text body of the email",
    html="<p>This is the html part of the email</p>",
    files=['file1.txt', 'file2.txt'])

Additionally, you can create a raw email messages and send it. See below for
more details.

***
API
***

.. autoclass:: parsons.notifications.gmail.Gmail
   :inherited-members:
   :members:

==========
SMTP
==========


********
Overview
********

The SMTP module enables the sending of email through a generic SMTP server. If you have an email server other
than Gmail this is likely the best way to send emails with Parsons.

.. note::

  Credentials
     - Credentials are required to use the class. You'll need to provide a valid username and password for
       the SMTP server you are using.

.. toctree::
    :maxdepth: 1

**********
QuickStart
**********

To initialize the SMTP class you will need to tell it how to connect to the SMTP server:


.. code-block:: python

 from parsons import SMTP

 smtp = SMTP(
     host="fake.host.com",
     port=9999,
     username="my_username",
     password="dont_use_this_password"
 )

.. note::

  Environment Variables
    - Instead of passing in values to initialize an instance of the SMTP class, you can set environment
      variables to hold the values. The names of the environment variables are the names of the arguments
      capitalized and prefixed with ``SMTP_``. For example, ``SMTP_HOST`` or ``SMTP_PASSWORD``. If both
      an environment variable and an initialization argument are present, the argument will take precedence.

The easiest way to send a message:

.. code-block:: python

  smtp.send_email(
      "sender@email.com",
      "recipient@email.com",
      "The Subject",
      "This is the text body of the email"
  )

The current version also supports sending html emails and emails with
attachments.

.. code-block:: python

  smtp.send_email(
      "sender@email.com",
      "recipient@email.com",
      "An html email with attachments",
      "This is the text body of the email",
      html="<p>This is the html part of the email</p>",
      files=['file1.txt', 'file2.txt']
  )

***
API
***

.. autoclass:: parsons.notifications.smtp.SMTP
   :inherited-members:
   :members:
   