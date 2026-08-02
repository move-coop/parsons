###############
Solidarity Tech
###############

Overview
========

Solidarity Tech's all-in-one nonprofit CRM includes digital tools like
texting, calling, email & websites for advocacy groups, unions & grassroots organizers.

As of September 2026, the :class:`~parsons.solidarity_tech.solidarity_tech.SolidarityTech` connector supports
all endpoints described in the `Solidarity Tech API Documentation <https://www.solidarity.tech/reference/solidarity-tech-api>`_.

Quickstart
==========

To instantiate the :class:`~parsons.solidarity_tech.solidarity_tech.SolidarityTech` class,
you can either store your Solidarity Tech bearer authorization key as
an environmental variable (``SOLIDARITY_TECH_BEARER_KEY``) or pass it as a keyword argument.

.. code-block:: python
   :caption: Load bearer authorization key from environment variable

   from parsons import SolidarityTech
   st = SolidarityTech()

.. code-block:: python
   :caption: Pass bearer authorization key as argument

   from parsons import SolidarityTech
   st = SolidarityTech(api_token='my_bearer_key')

You can then call various endpoints:

.. code-block:: python
   :caption: Get all events

   events = st.get_events()

.. code-block:: python
   :caption: Create a new user

   st.create_user(
       first_name="Elizabeth",
       last_name="Flynn",
       email="egflynn@example.com"
   )

API
====

.. autoclass:: parsons.solidarity_tech.solidarity_tech.SolidarityTech
   :inherited-members:
   :members:
