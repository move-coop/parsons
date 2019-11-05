Twilio
======

`Twilio <https://twilio.com>`_ is a messaging platform that allows you to send SMS messages, voice calls and
variety of other tools.


***********
Quick Start
***********

=================
Get Account Usage
=================

.. code-block:: python
	
	from parsons import Twilio

	twilio = Twilio()

	# Get usage last month
	twilio.get_account_usage(time_period='last_month')

	# Get usage for a specific date period
	twilio.get_account_usage(start_date='2019-10-01', end_date='2019-10-05')

	# Get usage for a specific resource
	twilio.get_account_usae(category='sms-inbound')

=================================
Get Inbound and Outbound Messages
=================================

.. code-block:: python
	
	from parsons import Twilio

	twilio = Twilio()

	# Get messages from a specific day
	twilio.get_messages(date_sent='10-01-2019')

	# Get messages sent to a specific phone number
	twilio.get_messages(to='9995675309')

***
API
***
.. autoclass :: parsons.Twilio
   :inherited-members: