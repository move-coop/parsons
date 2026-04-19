#####
Gmail
#####

Overview
========

The Gmail module leverages the Gmail API and provides an way to easily send
notifications through email. It is recommended that you reference the
`Gmail API documentation <https://developers.google.com/workspace/gmail/api/guides/>`__ for
additional details and information.

.. admonition:: Credentials and token

   - Credentials are required to use the class
   - You will need to pass in the path to the credentials and to where a
     generated token will be saved. Typically you’ll get the credentials from
     the Google Developer Console (look for the “Gmail API”).

.. admonition:: 6MB Attachment Size Limit

   - Currently there is a limit of 6MB when sending attachments.

Quickstart
==========

.. code-block:: python
   :caption: Configure credentials

   from parsons import Gmail
   gmail = Gmail(
      creds_path="~/secret_location/credentials.json",
      token_path="~/secret_location/token.json",
   )

.. code-block:: python
   :caption: Send an email

   gmail.send_email(
      "sender@email.com",
      "recipient@email.com",
      "The Subject",
      "This is the text body of the email",
   )

.. code-block:: python
   :caption: Send an email with HTML and/or attachments(s).

   gmail.send_email(
      "sender@email.com",
      "recipient@email.com",
      "An html email with attachments",
      "This is the text body of the email",
      html="<p>This is the html part of the email</p>",
      files=['file1.txt', 'file2.txt'],
   )

Additionally, you can create a raw email messages and send it. See below for
more details.

API
====

.. autoclass:: parsons.notifications.gmail.Gmail
   :inherited-members:
   :members:
