Salesforce
==========

********
Overview
********

`Salesforce <https://www.salesforce.com>`_ is a cloud-based CRM (customer relationship management) tool
with a huge share of the for-profit and apolitical non-profit markets. This Parsons integration with the
`Salesforce REST API <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_what_is_rest_api.htm>`_
provides methods to describe objects and fields, handle records, and submit Salesforce
`SOQL queries <https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm>`_
that return a Parsons Table.

The ``Salesforce`` class utilizes the `Simple Salesforce <https://simple-salesforce.readthedocs.io/en/latest/>`_
client for making API calls under the hood.

.. note::

  Authentication
    ``Salesforce`` requires your Salesforce username and password, as well as a security token
    which can be acquired or reset by logging in to your Salesforce account and navigating to
    *Settings > My Personal Information > Reset My Security Token*.

***********
Quick Start
***********

To instantiate the ``Salesforce`` class, you can store your Salesforce username, password,
and security token as environmental variables (``SALESFORCE_USERNAME``, ``SALESFORCE_PASSWORD``,
and ``SALESFORCE_SECURITY_TOKEN``, respectively) or pass them in as arguments:

.. code-block:: python

    from parsons import Salesforce, Table

    # First approach: Pass API credentials as environmental variables
    sf = Salesforce()

    # Second approach: Pass API credentials as arguments
    sf = Salesforce(username='my@email', password='my_password', security_token='123')

You can then call different endpoints:

.. code-block:: python

    # Get IDs and names for all Contacts
    all_contacts = sf.query("SELECT Id, firstname, lastname FROM Contact")

    # Get IDs, names, and email addresses from Contacts with a specific value for a custom field
    ak_contacts = sf.query("SELECT Id, firstname, lastname, email FROM Contact WHERE digital_source__c == 'AK'")

    # Update existing Contacts and create new records based on data in a Parsons Table
    upsert_results = sf.upsert('Contact', contacts_table, 'id')

***
API
***

.. autoclass:: parsons.salesforce.salesforce.Salesforce
   :inherited-members:
   :members:
   