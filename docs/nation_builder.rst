NationBuilder
==============

********
Overview
********

The NationBuilder class allows you to interact with the NationBuilder API. Users of this Parsons integration can download a full list of people, update and upsert people.

.. note::

   Authentication
      In order to use this class you need your nation slug and access token. To get your access token login to your nation and navigate to ``Settings > Developer > API Token`` and create a new token. You can get more info in the `NationBuilder API docs <https://nationbuilder.com/api_quickstart>`_.

==========
Quickstart
==========

To instantiate the NationBuilder class, you can either store your ``NB_SLUG`` and ``NB_ACCESS_TOKEN`` keys as environment
variables or pass them in as arguments:

.. code-block:: python

   from parsons import NationBuilder

   # First approach: Use API key environment variables

   # In bash, set your environment variables like so:
   # export NB_SLUG='my-nation-slug'
   # export NB_ACCESS_TOKEN='MY_ACCESS_TOKEN'
   nb = NationBuilder()

   # Second approach: Pass API keys as arguments
   nb = NationBuilder(slug='my-nation-slug', access_token='MY_ACCESS_TOKEN')

You can then make a request to get all people and save its data to a Parsons table using the method, ``get_people()``:

.. code-block:: python

    # Create Parsons table with people data from API
    parsons_table = nb.get_people()

    # Save people as CSV
    parsons_table.to_csv('people.csv')

The above example shows how to create a Parsons table with all people registered in your NationBuilder nation.

***
API
***

.. autoclass:: parsons.nation_builder.nation_builder.NationBuilder
   :inherited-members:
   :members:
   