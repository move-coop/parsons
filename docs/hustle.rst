Hustle
======

********
Overview
********

`Hustle <https://www.hustle.com/>`_ is a peer to peer texting communication platform. This Parsons integration with the
the `Hustle v1 API <https://api.hustle.com/docs/>`_ provides methods for fetching agents,
organizations, groups, leads, and tags, as well as creating and updating agents and leads.

.. note::

  Authentication
    Hustle uses the `OAuth2 client credentials flow <https://www.oauth.com/oauth2-servers/access-tokens/client-credentials/>`_.
    Clients with a Hustle account can obtain the client ID and client secret needed to request a token which
    grants to access the Hustle API for 2 hours before expiring.

    **Warning:** 10 failed attempts to generate an access token will result in a temporary block on your IP address, and
    100 failed attempts in 24 hour results in a permanent ban.

  API Limits
    There is a limit of 100 requests per second for endpoints returning resources.

***********
Quick Start
***********

To instantiate the ``Hustle`` class, you can either store your Hustle client ID and secret as environmental variables
(``HUSTLE_CLIENT_ID`` and ``HUSTLE_CLIENT_SECRET``, respectively) or pass them in as keyword arguments:

.. code-block:: python

    from parsons import Hustle

    # First approach: Use API credentials via environmental variables
    hustle = Hustle()

    # Second approach: Pass API credentials as arguments
    hustle = Hustle(client_id='MYID', client_secret='MYSECRET')

    # Export your groups to a csv
    tbl = hustle.get_groups(organization_id='ORGID')
    tbl.to_csv('my_hustle_groups.csv')

    # Export organizations to Redshift
    tbl.get_organizations().to_redshift('hustleschema.hustle_organizations')

    # Import leads from a csv
    leads = Table.from_csv('my_leads.csv')
    group_id = 'MYGROUP'
    hustle.create_leads(leads, group_id)

***
API
***

.. autoclass:: parsons.hustle.hustle.Hustle
   :inherited-members:
   :members:
   