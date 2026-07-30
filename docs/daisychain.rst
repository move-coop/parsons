##########
Daisychain
##########

Overview
========

`Daisychain <https://www.daisychain.app/>`_ is a digital organizing automation tool that allows organizers to string together automated digital outreach steps, similar to Zapier but designed specifically for digital organizing. The Parsons connector provides methods for finding contacts and triggering events through the Daisychain API.

This connector implements the ``people/match`` and ``actions`` endpoints of the Daisychain API, allowing you to find existing people records and post actions that can trigger automations.

.. admonition:: Getting Your API Key

   The Daisychain API uses API token authentication.
   You can generate your API token from your Daisychain account settings.

Quick Start
===========

To instantiate the class, you can either pass in the API token as an argument or set the ``DAISYCHAIN_API_TOKEN`` environmental variable.

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import Daisychain
   dc = Daisychain()

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import Daisychain
   dc = Daisychain(api_token='MY_API_TOKEN')

You can then call various endpoints:

.. code-block:: python
   :caption: Find a person by email address

    people = dc.find_person(email_address='person@example.com')

.. code-block:: python
   :caption: Find a person by phone number

    people = dc.find_person(phone_number='+15555551234')

.. code-block:: python
   :caption: Find a person by email and phone (AND logic)

   people = dc.find_person(email_address='person@example.com', phone_number='+15555551234')


.. code-block:: python
   :caption: Post an action to trigger an automation

    # Create a new person if they don't exist, or associate the action with an existing person
    person_id = dc.post_action(
        email_address='person@example.com',
        phone_number='+15555551234',
        first_name='Jane',
        last_name='Doe',
        email_opt_in=True,
        sms_opt_in=True,
        action_data={'type': 'petition_signature', 'petition_id': '12345'}
    )

.. code-block:: python
   :caption: Use action_data with custom fields to trigger specific automations

    # action_data can contain any JSON and be matched in Daisychain automation builder
    person_id = dc.post_action(
        email_address='volunteer@example.com',
        action_data={'event_type': 'volunteer_signup', 'event_id': 'canvass_2024'}
    )

API
===

.. autoclass :: parsons.daisychain.daisychain.Daisychain
   :inherited-members:
   :members:
