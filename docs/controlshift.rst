############
Controlshift
############

Overview
========

Controlshift is a platform for creating campaigns with distributed events,
local groups, and member-led petitions. This connector allows you to interact
with select functions of the the `ControlShift Authenticated REST API Documentation`_.

.. admonition:: Authentication

   An API Application Integration is required to instantiate the
   :class:`~parsons.controlshift.controlshift.Controlshift` class.
   Details on how to create the integration and acquire credentials
   can be found `ControlShift Authenticated REST API Documentation`_.

Quickstart
==========

To instantiate the Controlshift class, you can either store your credentials as environment
variables (``CONTROLSHIFT_HOSTNAME``, ``CONTROLSHIFT_CLIENT_ID``, and ``CONTROLSHIFT_CLIENT_SECRET``)
or pass them in as arguments:

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import Controlshift
   cs = Controlshift()

.. code-block:: python
   :caption: Pass API credentials as arguments

   from parsons import Controlshift
   cs = Controlshift(hostname='my_hostname', client_id='my_client_id', client_secret='my_client_secret')

.. code-block:: python
   :caption: Get all petitions

   cs.get_petitions()

API
====

.. autoclass:: parsons.controlshift.Controlshift
   :inherited-members:
   :members:

.. _ControlShift Authenticated REST API Documentation: https://developers.controlshiftlabs.com/#authenticated-rest-api
