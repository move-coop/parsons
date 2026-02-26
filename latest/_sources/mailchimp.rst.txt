Mailchimp
=========

********
Overview
********

`Mailchimp <https://www.mailchimp.com>`_ is a platform used for creating and sending mass emails.
`The Mailchimp API <https://developers.braintreepayments.com/>`_ allows users to interact with data from existing
email campaigns under their account and to configure further campaigns.

This Parsons integration focuses on accessing information about previous email campaigns, including methods for
fetching campaigns, members, emails, and unsubscribes.

.. note::

   Authentication
      Mailchimp requires an API key, which can be obtained from the 'API Keys' section of your Mailchimp
      account, assuming you have Manager privileges. For more information about Mailchimp authentication, see
      the Mailchimp help page about `API Keys <https://mailchimp.com/help/about-api-keys/>`_.

***********
Quick Start
***********

To instantiate the Mailchimp class, you can either store your Mailchimp API key
as an environmental variable (``MAILCHIMP_API_KEY``) or pass it as an argument.

.. code-block:: python

    from parsons import Mailchimp

    # First approach: API key is stored as an environmental variable
    mc = Mailchimp()

    # Second approach: Pass API key as argument
    mc = Mailchimp(api_key='my_api_key')

    # Get all recipient lists under a Mailchimp account
    lists = mc.get_lists()

    # Get campaigns sent since the beginning of 2020
    recent_campaigns = mc.get_campaigns(since_send_time='2020-01-01T00:00:00Z')

    # Get all unsubscribes from a campaign
    unsubscribes = mc.get_unsubscribes('dd693a3e74')

***
API
***

.. autoclass:: parsons.mailchimp.mailchimp.Mailchimp
   :inherited-members:
   :members:
   