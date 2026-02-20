Action Builder
==============

********
Overview
********

`Action Builder <https://actionbuilder.org/>`_ is an online tool for field organizing, with an
original use-case designed for the Labor context. While it has essentially no built-in outreach
capabilities, it does provide robust record and relationship storage, including the ability to
create custom record types. For more information, see
`Action Builder developer docs <https://www.actionbuilder.org/docs/v1/index.html>`_

.. note::

  Custom Fields/Tags
    Action Builder custom fields are treated as tags in both the SQL Mirror, and the API. This
    means that, with a couple exceptions such as date, values must be created ahead of time to be
    applied to a record. Each tag has two layers of taxonomy above it as well, that appear slightly
    differently in the SQL Mirror and in the API. In the SQL Mirror, each tag has a
    ``tag_category``, and each category has a ``tag_group``. In the API, the equivalents are called
    ``tag_field`` and ``tag_section``, respectively (closer to the naming in the UI). Tags can be
    applied on Connections as well as on Entities.

***********
Quick Start
***********

To instantiate a class, you can either pass in the API token as an argument or set the
``ACTION_BUILDER_API_TOKEN`` environmental variable. The subdomain at which you access the UI must
also be provided. If all calls from this object will be to the same Campaign in Action Builder,
an optional campaign argument may also be supplied. If not supplied when instantiating, campaign
may be passed to individual methods, instead.

.. code-block:: python

   from parsons import ActionBuilder

   # First approach: Use API credentials via environmental variables
   bldr = ActionBuilder(subdomain='yourorgsubdomain')

   # Second approach: Pass API credentials as arguments
   bldr = ActionBuilder(api_token='MY_API_TOKEN', subdomain='yourorgsubdomain')

   # Third approach: Include campaign argument
    bldr = ActionBuilder(
        api_token = 'MY_API_TOKEN',
        subdomain = 'yourorgsubdomain',
        campaign = 'your-desired-campaign-id'
    )

You can then call various endpoints:

.. code-block:: python

    # Assuming instantiation with campaign provided

    # List all tags stored in the provided Action Builder campaign
    all_tags = bldr.get_campaign_tags()

    # Add a new tag value to the options available for the the field
    bldr.insert_new_tag(
        tag_name = 'Mom's Phone', # This is new
        tag_field = 'Favorite Toy', # This would already exist, created in the UI
        tag_section = 'Preferences' # This would already exist, created in the UI
    )

    # Add a person record to the provided Action Builder campaign
    bldr.upsert_entity(
        entity_type = 'Person',
        data = {"person": {"given_name": "Rory"}}
    )

    # Connect two records and apply some tags to the Connection
    tag_data = { # All of the values below must already have been created
        "action_builder:name": "Friend of the Family",
        "action_builder:field": "Relationship",
        "action_builder:section": "People to People Info"
    }

    bldr.upsert_connection(
        ["entity-interact-id-1", "entity-interact-id-2"], # Any two entity IDs
        tag_data = tag_data
    )

***
API
***

.. autoclass:: parsons.action_builder.action_builder.ActionBuilder
   :inherited-members:
   :members:
   