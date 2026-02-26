CapitolCanary
=============

********
Overview
********

`CapitolCanary <https://capitolcanary.com/>`_ is a digital advocacy tool used by progressive organizations. This class
allows you to interact with the tool by leveraging their `API <http://docs.phone2action.com/#overview>`_.

.. note::

  Authentication
   You will need to email CapitolCanary to request credentials to access the API. The credentials consist of an app ID and an app key.

***********
Quick Start
***********

To instantiate the ``CapitolCanary`` class, you can either pass in the app ID and app key as arguments or set the
``CAPITOLCANARY_APP_ID`` and ``CAPITOLCANARY_APP_KEY`` environmental variables.

.. code-block:: python

   from parsons import CapitolCanary

   # Instantiate the class using environment variables
   cc = CapitolCanary()

   # Get all advocates updated in the last day
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

***
API
***

.. autoclass:: parsons.capitol_canary.capitol_canary.CapitolCanary
   :inherited-members:
   :members:
   