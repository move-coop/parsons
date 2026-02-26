Quickbase
=========

********
Overview
********

Quickbase is a workflow automation and data warehousing tool. This class allows you to interact
with select functions of the the `Quickbase API <https://developer.quickbase.com/>`_ .

This Parsons connector provides methods to fetch lists of available tables in Quickbase, and to
query those tables using `Quickbase's own query language
<https://help.quickbase.com/api-guide/componentsquery.html>`_.

.. note::

  Authentication
    A user token and app ID are required to instantiate the ``Quickbase`` class.
    Details on how to create user tokens can be found `on the Quickbase website
    <https://help.quickbase.com/user-assistance/create_user_tokens.html>`_.

**********
Quickstart
**********

To instantiate the Quickbase class, you can either store your credentials as environment
variables (``QUICKBASE_HOSTNAME`` and ``QUICKBASE_USER_TOKEN``) or pass them in as arguments:

.. code-block:: python

   from parsons import Quickbase

   # First approach: Use API credentials via environmental variables
   qb = Quickbase()

   # Second approach: Pass API credentials as arguments
   qb = Quickbase(hostname='my_hostname', user_token='my_token')

   # Get all tables available from a Quickbase app
   qb.get_app_tables(app_id='my_app_id')

   # Get all data from a given table
   qb.query_records(table_from='my_table_id')

***************
Quickbase Class
***************

.. autoclass:: parsons.quickbase.quickbase.Quickbase
   :inherited-members:
   :members:
   