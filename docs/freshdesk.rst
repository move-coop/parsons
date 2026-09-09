#########
Freshdesk
#########

Overview
========

`Freshdesk <https://www.freshworks.com/freshdesk>`__ is an omnichannel customer support platform.
This Parsons integration with the `Freshdesk API <https://developers.freshdesk.com/api/>`__
provides methods to fetch tickets, contacts, companies, and agents. Results are returned
as Parsons Tables.

.. admonition:: Authentication

   To use the :class:`~parsons.freshdesk.freshdesk.Freshdesk` class,
   you must provide the subdomain of your Freshdesk account and an API Key,
   which can be found by logging into Freshdesk and following the instructions in the
   `API documentation <https://support.freshdesk.com/support/solutions/articles/215517-how-to-find-your-api-key>`__.

.. admonition:: Rate Limits

   Rate limits depend on your Freshdesk plan, so be sure to check the API documentation for your
   `rate limits <https://developers.freshdesk.com/api/#ratelimit>`__ and follow the
   `best practices guide <https://developers.freshdesk.com/api/#best_practices>`__ to avoid exceeding them.

Quickstart
==========

To instantiate the Freshdesk class, you can either store your Freshdesk domain and API
Key as environmental variables (``FRESHDESK_DOMAIN`` and ``FRESHDESK_API_KEY``, respectively)
or pass them in as keyword arguments:

.. code-block:: python
   :caption: Use environmental variables

   from parsons import Freshdesk
   freshdesk = Freshdesk()

.. code-block:: python
   :caption: Use keyword arguments

   from parsons import Freshdesk
   freshdesk = Freshdesk(domain='my_domain', api_key='my_api_key')

You can then call various endpoints:

.. code-block:: python
   :caption: Fetch all tickets requested by a individual based on their email

   freshdesk.get_tickets(requester_email='user@email.com')

.. code-block:: python
   :caption: Fetch all contacts in a specific company

   freshdesk.get_contacts(company_id='123')

.. code-block:: python
   :caption: Fetch a specific agent by their mobile number

   freshdesk.get_agents(mobile='7654367287')

API
====

.. autoclass:: parsons.freshdesk.freshdesk.Freshdesk
   :inherited-members:
   :members:
