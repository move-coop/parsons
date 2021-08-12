Bluelink
=============

********
Overview
********

`Bluelink <https://bluelink.org/>`_ is an online tool for connecting the various `digital software tools <https://https://bluelink.org/product/#integrations>`_
used by campaigns and movement groups in the political and non-profit space to allow you to seamlessly and easily sync data between them.
This integration currently supports sending your structured person data and related tags to Bluelink, after which you can use our UI to send to any of our
`supported tools <https://bluelink.org/product/#integrations>`_. If you don't see a tool you would like to connect to, please reach out at
hello@bluelink.org to ask us to add it.

.. note::
   Authentication
      If you don't have a Bluelink account please complete the `form <https://bluelink.org/#form>`_ on our website or email us at hello@bluelink.org.
      To get connection credentials select or ask an account administrator to select `Bluelink Webhook <https://app.bluelink.org/bluelink-webhook-integration>`_
      from the apps menu. The credentials are automatically embedded into a one time secret link in case they need to be sent to you.
      Open the link to access the user and password, that you will then either pass directly to the Bluelink connector as arguments, 
      or set them as environment variables.

==========
Quickstart
==========

To instantiate a class, you can either pass in the user and password token as arguments or set them in the
BLUELINK_WEBHOOK_USER and BLUELINK_WEBHOOK_PASSWORD environment variables.

.. code-block:: python

   from parsons.bluelink import Bluelink

   # First approach: Use API credentials via environmental variables
   bluelink = Bluelink()

   # Second approach: Pass API credentials as arguments
   bluelink = Bluelink('username', 'password')

You can upsert Person data by directly using a Person object:

.. code-block:: python

   from parsons.bluelink import Bluelink, Person, Identifier

   # create the person object
   person = Person(identifiers=[Identifier(source="SOURCE_VENDOR", identifier="ID")], given_name="Jane", family_name="Doe")

   # use the bluelink connector to upsert
   source = "MY_ORG_NAME"
   bluelink.upsert_person(source, person)

You can bulk upsert person data via a Parsons Table by providing a function that takes a row and outputs a Person:

.. code-block:: python

   from parsons.bluelink import Bluelink, Person, Identifier

   # a function that takes a row and returns a Person
   def row_to_person(row):
      return Person(identifiers=[Identifier(source="SOURCE_VENDOR", identifier=row["id"])],
                    given_name=row["firstName"], family_name=row["lastName"])

   # a parsons table filled with person data
   parsons_tbl = get_data()

   # call bulk_upsert_person
   source = "MY_ORG_NAME"
   bluelink.bulk_upsert_person(source, parsons_tbl, row_to_person)

***
API
***

.. autoclass :: parsons.bluelink.Bluelink
   :inherited-members:
