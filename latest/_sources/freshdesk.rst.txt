Freshdesk
=========

********
Overview
********

`Freshdesk <https://freshdesk.com>`_ is an omnichannel customer support platform.
This Parsons integration with the `Freshdesk API <https://developers.freshdesk.com/api/>`_
provides methods to fetch tickets, contacts, companies, and agents. Results are returned
as Parsons Tables.

.. note::

   Authentication
      To use the ``Freshdesk`` class, you must provide the subdomain of your Freshdesk account and an API Key,
      which can be found by logging into Freshdesk and following the instructions in the
      `API documentation <https://support.freshdesk.com/support/solutions/articles/215517-how-to-find-your-api-key>`_.

.. note::

   Rate Limits
      Rate limits depend on your Freshdesk plan, so be sure to check the API documentation for your
      `rate limits <https://developers.freshdesk.com/api/#ratelimit>`_ and follow the
      `best practices guide <https://developers.freshdesk.com/api/#best_practices>`_ to avoid exceeding them.

**********
Quickstart
**********

To instantiate the Freshdesk class, you can either store your Freshdesk domain and API
Key as environmental variables (``FRESHDESK_DOMAIN`` and ``FRESHDESK_API_KEY``, respectively)
or pass them in as keyword arguments:

.. code-block:: python

   from parsons import Freshdesk

   # First approach: Use environmental variables
   freshdesk = Freshdesk()

   # Second approach: Use keyword arguments
   freshdesk = Freshdesk(domain='my_domain', api_key='my_api_key')

You can then call various endpoints:

.. code-block:: python

    # Fetch all tickets requested a individual based on their email
    freshdesk.get_tickets(requester_email='user@email.com')

    # Fetch all contacts in a specific company
    freshdesk.get_contacts(company_id='123')

    # Fetch a specific agent by their mobile number
    freshdesk.get_agents(mobile='7654367287')

***
API
***

.. autoclass:: parsons.freshdesk.freshdesk.Freshdesk
   :inherited-members:
   :members:
   