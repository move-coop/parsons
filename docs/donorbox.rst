Donorbox
========

********
Overview
********

`Donorbox <https://donorbox.org/>`_ is an online donation platform through which donors can make one-off or
recurring donations. This Parsons class provides methods for extracting donors, campaigns, donations, and plans.

The documentation for the underlying Donorbox API can be found `here <https://github.com/donorbox/donorbox-api>`_.

.. note::

    To authenticate, go to your account on donorbox.org and select the "API & Zapier Integration" option
    under Add-ons. Enable the add-on. (Note that currently Donorbox charges to enable this feature.)
    Once the add-on is enabled, hit the "Set new API key" button and copy the generated key.

**********
Quickstart
**********

To instantiate the Donorbox class, you can either store the Donorbox accont email and
API key as environmental variables (``DONORBOX_ACCOUNT_EMAIL``, ``DONORBOX_API_KEY``)
or pass them in as arguments:

.. code-block:: python

   from parsons import Donorbox

   # First approach: Use API key and account email via environmental variables
   donorbox = Donorbox()

   # Second approach: Pass API credentials and user email as arguments
   donorbox = Donorbox(email='me@myorg.com', api_key='MYAPIKEY')

You can then call various endpoints:

.. code-block:: python

    # Get campaigns

    campaigns = donorbox.get_campaigns()                                    # get all campaigns
    campaigns = donorbox.get_campaigns(name="My campaign")                  # get campaigns by name
    campaigns = donorbox.get_campaigns(name="My campaign", order="desc")    # results in descending order

    # Get donations

    donations = donorbox.get_donations()                                    # get all donations
    donations = donorbox.get_donations(date_to="2022-10-22")                # get all donations before date
    donations = donorbox.get_donations(campaign_name="My campaign")         # filter donations by campaign

    # Get donors

    donors = donorbox.get_donors()                                          # get all donors
    donors = donorbox.get_donors(email="example@example.org")               # get donors by email
    donors = donorbox.get_donors(page=1, per_page=10)                       # use pagination

    # Get plans

    plans = donorbox.get_plans()                                            # get all plans
    plans = donorbox.get_plans(date_from="2022-10-22")                      # get plans started after date


***
API
***

.. autoclass:: parsons.donorbox.donorbox.Donorbox
   :inherited-members:
   :members:
   