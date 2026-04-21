####
SMTP
####

Overview
========

The SMTP module enables the sending of email through a generic SMTP server.
If you have an email server other than Gmail,
this is likely the best way to send emails with Parsons.

.. admonition:: Credentials

   Credentials are required to use the class.
   You'll need to provide a valid username and password for the SMTP server you are using.

Quickstart
==========

To initialize the SMTP class you will need to tell it how to connect to the SMTP server:

.. code-block:: python
   :caption: Configure server connection

   from parsons import SMTP
   smtp = SMTP(
      host="fake.host.com",
      port=9999,
      username="my_username",
      password="dont_use_this_password",
   )

.. admonition:: Environment Variables

   Instead of passing in values to initialize an instance of the SMTP class, you can set environment
   variables to hold the values. The names of the environment variables are the names of the arguments
   capitalized and prefixed with ``SMTP_``. For example, ``SMTP_HOST`` or ``SMTP_PASSWORD``. If both
   an environment variable and an initialization argument are present, the argument will take precedence.

.. code-block:: python
   :caption: Send an email

   smtp.send_email(
      "sender@email.com",
      "recipient@email.com",
      "The Subject",
      "This is the text body of the email",
   )

.. code-block:: python
   :caption: Send an email with HTML and/or attachment(s).

   smtp.send_email(
      "sender@email.com",
      "recipient@email.com",
      "An html email with attachments",
      "This is the text body of the email",
      html="<p>This is the html part of the email</p>",
      files=['file1.txt', 'file2.txt'],
   )

API
====

.. autoclass:: parsons.notifications.smtp.SMTP
   :inherited-members:
   :members:
