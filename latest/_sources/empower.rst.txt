Empower
=======

********
Overview
********

The Empower class allows you to interact with the Empower API. Documentation for the Empower API can be found
in their `GitHub <https://github.com/getempower/api-documentation/blob/master/README.md>`_ repo.

The Empower API only has a single endpoint to access all account data. As such, it has a very high overhead. This
connector employs caching in order to allow the user to specify the tables to extract without additional API calls.
You can disable caching as an argument when instantiating the class.

.. note::

    To authenticate, request a secret token from Empower.

==========
Quickstart
==========

To instantiate the Empower class, you can either store your ``EMPOWER_API_KEY`` as an environment
variables or pass it in as an argument:

.. code-block:: python

   from parsons import Empower

   # First approach: Use API key environment variables

   # In bash, set your environment variables like so:
   # export EMPOWER_API_KEY='MY_API_KEY'
   empower = Empower()

   # Second approach: Pass API keys as arguments
   empower = Empower(api_key='MY_API_KEY')

You can then request tables in the following manner:

.. code-block:: python

    tbl = empower.get_profiles()

***
API
***

.. autoclass:: parsons.empower.empower.Empower
   :inherited-members:
   :members:
   