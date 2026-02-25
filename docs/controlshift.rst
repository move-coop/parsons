Controlshift
============

********
Overview
********

Controlshift is a platform for creating campaigns with distributed events, local groups, and member-led petitions. This connector allows you to interact with select functions of the the `Controlshift Authenticated REST API <https://developers.controlshiftlabs.com/#authenticated-rest-api/>`_ .

.. note::

  Authentication
    An API Application Integration is required to instantiate the ``Controlshift`` class.
    Details on how to create the integration and acquire credentials can be found `on the Controlshift website
    <https://developers.controlshiftlabs.com/#authenticated-rest-api-quickstart-guide>`_.

**********
Quickstart
**********

To instantiate the Controlshift class, you can either store your credentials as environment
variables (``CONTROLSHIFT_HOSTNAME``, ``CONTROLSHIFT_CLIENT_ID``, and ``CONTROLSHIFT_CLIENT_SECRET``) or pass them in as arguments:

.. code-block:: python

   from parsons import Controlshift

   # First approach: Use API credentials via environmental variables
   cs = Controlshift()

   # Second approach: Pass API credentials as arguments
   cs = Controlshift(hostname='my_hostname', client_id='my_client_id', client_secret='my_client_secret')

   # Get all petitions
   cs.get_petitions()

******************
Controlshift Class
******************

.. autoclass:: parsons.controlshift.Controlshift
   :inherited-members:
   :members:
   