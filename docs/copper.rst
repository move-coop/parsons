######
Copper
######

Overview
========

`Copper <https://copper.com>`_ is a customer relationship management (CRM) platform to track individuals, companies
and activity data. This Parsons class provides methods for extracting people, companies and actions.

.. admonition:: Getting Your API Key

   - Sign into Copper
   - Click on ``Settings`` (gear icon) and then ``API Keys``
   - Click the ``GENERATE API KEY`` button

Quickstart
==========

To instantiate the Copper class, you can either store the Copper user email and
API key as environmental variables (``COPPER_USER_EMAIL``, ``COPPER_API_KEY``)
or pass them in as arguments:

.. code-block:: python
   :caption: Use API key and user email via environmental variables

   from parsons import Copper
   copper = Copper()

.. code-block:: python
   :caption: Pass API credentials and user email as arguments

   from parsons import Copper
   copper = Copper(user_email='me@myorg.com', api_key='MYAPIKEY')

You can then call various endpoints:

.. code-block:: python
   :caption: Get people

   # This will unpack the people json as a dict of Parsons Tables.
   people_tbls = copper.get_people()

   # You can then save the tables as csvs
   for k, v in people_tbls.items():
      v.to_csv(f'{k}_copper.csv')

   # Or you send the tables to a database
   pg = Postgres()
   for k, v in people_tbls.items():
      v.to_postgres(f'copper.{k}', if_exists='drop')

.. code-block:: python
   :caption: Get companies

   # Get companies modified since a date, unix time. This will unpack the companies
   json as a dict of Parsons Tables.
   company_tbls = copper.get_companies({'minimum_modified_date': 1599674523})

API
====

.. autoclass:: parsons.copper.copper.Copper
   :inherited-members:
   :members:
