Braintree
=========

********
Overview
********

`Braintree <https://www.braintreepayments.com>`_ is an online payment processor often integrated in other
third-party donation platforms like ActionKit, etc.  Even if much data is accessible through those other
platforms things like credit card disputes and disbursement (to your bank account!) timing may only be
available directly through Braintree.

While much of the `Braintree API <https://developers.braintreepayments.com/>`_ is about processing payments,
this Parsons integration focuses on the record searching aspects. Specifically, the ``Braintree`` class provides
methods for fetching disputes and transactions.

.. note::

  Authentication
    Braintree authentication requires a Merchant ID, Public Key, and Private Key. These can be obtained by logging
    in to the Braintree `Control Panel <https://www.braintreegateway.com/login?_ga=1.85874009.1956923370.1599919088>`_,
    clicking on the gear icon in the top right corner, and finding each of the credentials as follows:

    1. **Merchant ID:** Click 'Business' and find your Merchant ID at the top of this page.
    2. **Public API Key:** Click 'API' and scroll to 'API Keys'. If there are none, click 'Generate New API Key'.
    3. **Private API Key:** Click 'API', scroll to 'API Keys', and click the 'view' link in the private column.

    For more information, see the `API documentation <https://articles.braintreepayments.com/control-panel/important-gateway-credentials>`_.

***********
Quick Start
***********

To instantiate the Braintree class, you can either store your Merchant ID, Public API
Key, and Private API Key as environmental variables (``BRAINTREE_MERCHANT_ID``,
``BRAINTREE_PUBLIC_KEY``, and ``BRAINTREE_PRIVATE_KEY``, respectively) or pass them in
as arguments:

.. code-block:: python

    from parsons import Braintree

    # First approach: Use API credentials via environmental variables
    brains = Braintree()

    # Second approach: Pass API credentials as arguments
    brains = Braintree(merchant_id='my_merchant_id', public_key='my_public_key', private_key='my_private_key')

    # Get disputes from a single day
    disputes = brains.get_disputes('2020-01-01', '2020-01-02')

    # Get disbursements from a single day
    disbursements = brains.get_transactions(disbursement_start_date='2020-01-01',
                                            disbursement_end_date='2020-01-02')

***
API
***

.. autoclass:: parsons.braintree.braintree.Braintree
   :inherited-members:
   :members:
   