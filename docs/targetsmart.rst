TargetSmart
============

********
Overview
********

`TargetSmart <https://targetsmart.com/>`_ provides access to voter and consumer data for the progressive community. Currently,
there are two TargetSmart services that are supported by two Parsons classes, each requiring separate credentials:

1. ``TargetSmartAPI``: `Single record lookup with HTTPS <https://docs.targetsmart.com/developers/tsapis/index.html>`_. This class provides methods to support searching for individual people, voters, and district information for a geographic location.
2. ``TargetSmartAutomation``: `Bulk record matching with SFTP <https://docs.targetsmart.com/developers/automation/index.html>`_. This class provides general methods for processing files instead of individual records.

.. note::
  Authentication
    Log in to `My TargetSmart <https://my.targetsmart.com/>`_ to access authentication credentials. You will need an API key
    to use the ``TargetSmartAPI`` class, and an SFTP username and password to use the ``TargetSmartAutomation`` class.

    For more information, see the `API documentation <https://docs.targetsmart.com/developers/tsapis/authentication.html>`_.

.. warnings::
  Returned fields
    Returned fields are controlled by the TargetSmart staff. Please contact them if adjustments are needed.

  Endpoint Access
    Access to endpoints is individually provisioned. If you encounter errors accessing an endpoint, please contact
    your TargetSmart account representative to verify that your API key has been provisioned access.

***********
TargetSmart
***********

==========
Quickstart
==========

To instantiate ``TargetSmartAPI``, you can either store your API Key as the environmental variable
``TS_API_KEY``, or pass it in as an argument:

.. code-block:: python

   from parsons import TargetSmartAPI

   # First approach: Store API key as an environmental variable
   ts_api = TargetSmartAPI()

   # Second approach: Pass API key as an argument
   ts_api = TargetSmartAPI(api_key='my_api_key')

You can then call various endpoints:

.. code-block:: python

   # Search for a person record using an email address
   ts_api.data_enhance(search_id='test@email.com', search_id_type='email')

   # Search for district information using an address
   ts_api.district(search_type='address', address='123 test st, Durham NC 27708')

===
API
===

.. autoclass :: parsons.TargetSmartAPI
   :inherited-members:

**********
Automation
**********

==========
Quickstart
==========

To instantiate ``TargetSmartAutomation``, you can either store your SFTP username and password
as the environmental variables ``TS_SFTP_USERNAME`` and ``TS_SFTP_PASSWORD``, or pass them in as
keyword arguments:

.. code-block:: python

   from parsons import TargetSmartAutomation

   # First approach: Store SFTP username and password as environmental variables
   ts_auto = TargetSmartAutomation()

   # Second approach: Pass SFTP username and password as arguments
   ts_auto = TargetSmartAutomation(username='my_sftp_username', password='my_sftp_password')

You can then call various endpoints:

.. code-block:: python

   # Check the status of a match job
   ts_auto.match_status(job_name='my_job_name')

   # Remove all files for the match job
   ts_auto.remove_files(job_name='my_job_name')

===
API
===

.. autoclass :: parsons.TargetSmartAutomation
   :inherited-members:
