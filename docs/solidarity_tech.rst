###############
Solidarity Tech
###############

Overview
========

What is Solidarity Tech?
------------------------

`Solidarity Tech`_'s all-in-one nonprofit CRM includes digital tools like
`texting <https://www.solidarity.tech/texting>`__,
`calling <https://www.solidarity.tech/calling>`__,
`email <https://www.solidarity.tech/email>`__ &
`websites <https://www.solidarity.tech/website>`__ for
`advocacy groups <https://www.solidarity.tech/for/advocacy>`__,
`unions <https://www.solidarity.tech/for/unions>`__ &
grassroots organizers.

The SolidarityTech Connector
----------------------------

As of September 2026, parsons' :class:`~parsons.solidarity_tech.solidarity_tech.SolidarityTech` connector supports
all endpoints described in the `Solidarity Tech API Documentation <https://www.solidarity.tech/reference/solidarity-tech-api>`_.
The documented `rate limits <https://www.solidarity.tech/reference/solidarity-tech-api#api-authorization--rate-limits>`__
are applied automatically, although advanced configuration is available.

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
   st = SolidarityTech(api_token='SOME_BEARER_KEY')

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

.. automodule:: parsons.solidarity_tech.exceptions
   :inherited-members:
   :members:

.. automodule:: parsons.solidarity_tech.enums
   :inherited-members:
   :members:

.. _Solidarity Tech: https://www.solidarity.tech/
