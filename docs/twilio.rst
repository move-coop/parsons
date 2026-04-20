######
Twilio
######

Overview
========

`Twilio <https://www.twilio.com>`__ is a messaging platform that allows you to programmatically
send and receive SMS messages, send and receive voice calls, and perform other communication
functions. This Parsons integration provides methods for fetching messages, accounts, and
account usage data.

.. admonition:: Authentication

   Twilio requires an account SID and an authorization token, which can be found in the
   `Admin Console <https://www.twilio.com/login?g=%2Fconsole%3F&t=2b1c98334b25c1a785ef15b6556396290e3c704a9b57fc40687cbccd79c46a8c>`__.
   For more information about authentication, see the `Twilio API documentation <https://www.twilio.com/docs/iam/credentials/api>`__.

Quickstart
==========

To instantiate the :class:`~parsons.twilio.twilio.Twilio` class, you can either store your Twilio account SID
and authorization token as environmental variables (``TWILIO_ACCOUNT_SID`` and
``TWILIO_AUTH_TOKEN``, respectively) or pass them in as arguments.

.. code-block:: python
   :caption: Pass credentials via environmental variables

   from parsons import Twilio
   twilio = Twilio()

.. code-block:: python
   :caption: Pass credentials as arguments

   from parsons import Twilio
   twilio = Twilio(account_sid='account_sid', auth_token='my_auth_token')

You can then call class methods:

.. code-block:: python
   :caption: Get usage last month

   twilio.get_account_usage(time_period='last_month')

.. code-block:: python
   :caption: Get usage for a specific date period

   twilio.get_account_usage(start_date='2019-10-01', end_date='2019-10-05')

.. code-block:: python
   :caption: Get usage for a specific resource

   twilio.get_account_usage(category='sms-inbound')

.. code-block:: python
   :caption: Get messages from a specific day

   twilio.get_messages(date_sent='10-01-2019')

.. code-block:: python
   :caption: Get messages sent to a specific phone number

   twilio.get_messages(to='9995675309')

API
====

.. autoclass:: parsons.twilio.twilio.Twilio
   :inherited-members:
   :members:
