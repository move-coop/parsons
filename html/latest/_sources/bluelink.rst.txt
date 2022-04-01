Bluelink
=============

********
Overview
********

`Bluelink <https://bluelink.org/>`_ is an online tool for connecting various `digital software tools <https://https://bluelink.org/product/#integrations>`_ used by campaigns and movement groups in the political and non-profit space so you can sync data between them. This integration currently supports sending your structured person data and related tags to Bluelink via the `Bluelink Webhook API <https://bluelinkdata.github.io/docs/BluelinkApiGuide#webhook>`_, after which you can use Bluelink's UI to send to any of their `supported tools <https://bluelink.org/product/#integrations>`_. If you don't see a tool you would like to connect to, please reach out at hello@bluelink.org to ask them to add it.

.. note::
   Authentication
      If you don't have a Bluelink account please complete the `form <https://bluelink.org/#form>`_ on the Bluelink website or email them at hello@bluelink.org. To get connection credentials select `Bluelink Webhook <https://app.bluelink.org/bluelink-webhook-integration>`_ from the apps menu. If you don't see this option, you may need to ask an account administrator to do this step for you.

      The credentials are automatically embedded into a one time secret link in case they need to be sent to you. Open the link to access the user and password.

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

You can upsert person data by directly using a BluelinkPerson object:

.. code-block:: python

   from parsons.bluelink import Bluelink, BluelinkPerson, BluelinkIdentifier

   # create the person object
   person = BluelinkPerson(identifiers=[BluelinkIdentifier(source="SOURCE_VENDOR", identifier="ID")], given_name="Jane", family_name="Doe")

   # use the bluelink connector to upsert
   source = "MY_ORG_NAME"
   bluelink.upsert_person(source, person)

You can bulk upsert person data via a Parsons Table by providing a function that takes a row and outputs a BluelinkPerson:

.. code-block:: python

   from parsons.bluelink import Bluelink, BluelinkPerson, BluelinkIdentifier

   # a function that takes a row and returns a BluelinkPerson
   def row_to_person(row):
      return BluelinkPerson(identifiers=[BluelinkIdentifier(source="SOURCE_VENDOR", identifier=row["id"])],
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
