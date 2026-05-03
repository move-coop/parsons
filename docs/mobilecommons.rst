#############
MobileCommons
#############

Overview
========

`MobileCommons <https://secure.mcommons.com/>`__ is a broadcast text messaging tool that helps orgranizations
mobilize supporters and fundraise by building opt-ed in audiences. You can read more about the product
`here <https://uplandsoftware.com/mobile-messaging/>`__.

Quickstart
==========

To instantiate a class you must pass the username and password of a MobileCommons account as an argument
or store the username and password into environmental variables called ``MOBILECOMMONS_USERNAME`` and
``MOBILECOMMONS_PASSWORD``, respectively. If you MobileCommons account has access to various MobileCommons
companies (i.e. organizations), you'll need to specify which MobileCommons company you'd like to interact
with by specifying the Company ID in the ``company_id`` parameter. To find the Company ID, navigate to the
`Company and Users page <https://secure.mcommons.com/companies/>`__.

.. code-block:: python
   :caption: Pass credentials via environmental variables for account has access to only one MobileCommons company

   from parsons import MobileCommons
   mc = MobileCommons()

.. code-block:: python
   :caption: Pass credentials via environmental variables for account has access to multiple MobileCommons companies

   from parsons import MobileCommons
   mc = MobileCommons(company_id='EXAMPLE78363BOCA483954419EB70986A68888')

.. code-block:: python
   :caption: Pass credentials via argument for account has access to only one MobileCommons company

   from parsons import MobileCommons
   mc = MobileCommons(username='octavia.b@scifi.net', password='badpassword123')

Then you can call various endpoints:

.. code-block:: python
   :caption: Return all MobileCommons subscribers in a table

   subscribers = get_campaign_subscribers(campaign_id=1234567)

.. code-block:: python
   :caption: Create a new profile, return profile_id

   new_profile=create_profile(phone=3073991987, first_name='Jane', last_name='Fonda')

API
====

.. autoclass:: parsons.mobilecommons.mobilecommons.MobileCommons
   :inherited-members:
   :members:
