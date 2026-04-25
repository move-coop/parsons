#############
CapitolCanary
#############

Overview
========

`CapitolCanary <https://capitolcanary.com/>`__ is a digital advocacy tool used by progressive organizations.
This class allows you to interact with the tool by leveraging the `Phone2Docs API <https://docs.phone2action.com>`__.

.. admonition:: Authentication

   You will need to email CapitolCanary to request credentials to access the API.
   The credentials consist of an app ID and an app key.

Quickstart
==========

To instantiate the :class:`~parsons.capitol_canary.capitol_canary.CapitolCanary` class,
you can either pass in the app ID and app key as arguments or set the
``CAPITOLCANARY_APP_ID`` and ``CAPITOLCANARY_APP_KEY`` environmental variables.

.. code-block:: python
   :caption: Instantiate the class using environment variables

   from parsons import CapitolCanary
   cc = CapitolCanary()

.. code-block:: python
   :caption: Get all advocates updated in the last day and opt them into SMS

   import datetime
   today = datetime.datetime.utcnow()
   yesterday = today - datetime.timedelta(days=1)

   # get_advocates returns a dictionary that maps the advocate data (e.g. phones) to a parsons
   # Table with the data for each advocate
   advocates_data = cc.get_advocates(updated_since=yesterday)

   # For all of our advocates' phone numbers, opt them into SMS
   for phone in advocates_data['phones']:
      phone_number = phone['phones_address']
      # Only update phone numbers that aren't already subscribed
      if phone['subscribed']:
         cc.update_advocate(phone['advocate_id'], phone=phone_number, sms_opt_in=True)

API
====

.. autoclass:: parsons.capitol_canary.capitol_canary.CapitolCanary
   :inherited-members:
   :members:

.. _Phone2Action API Create Advocate Documentation: https://docs.phone2action.com/#calls-create
