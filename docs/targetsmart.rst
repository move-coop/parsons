TargetSmart
============

`TargetSmart <https://targetsmart.com/>`_ provides access to voter and consumer data for the progressive community. Currently,
there are two TargetSmart services that are supported by two Parsons classes, since each requires separate credentials:

1. ``TargetSmartAPI``: `Single record lookup with HTTPS <https://docs.targetsmart.com/developers/tsapis/index.html>`_.
This class provides methods to support searching for individual people, voters, and district information for a geographic location.
2. ``TargetSmartAutomation``: `Bulk record matching with SFTP <https://docs.targetsmart.com/developers/automation/index.html>`_.
This class provides general methods for processing files instead of individual records.

.. note::
  Authentication
    Log in to `My TargetSmart <https://my.targetsmart.com/>`_ to access API keys. For more information, see the
    `API documentation <https://docs.targetsmart.com/developers/tsapis/authentication.html>`_.

.. warning:: 
   Returned fields
      Returned fields are controlled by the TargetSmart staff. Please contact them if adjustments are needed.

*******
API 2.0
*******

.. warning:: 
   Endpoint Access
      Access to endpoints is individually provisioned. If you encounter errors accessing an endpoint, please contact
      your TargetSmart account representative to verify that your API key have been provisioned access.

.. autoclass :: parsons.TargetSmartAPI
   :inherited-members:

**********
Automation
**********

In order to instantiate the class you must pass valid kwargs or store the following
environmental variables:

* ``'TS_SFTP_USERNAME'``
* ``'TS_SFTP_PASSWORD'``

.. autoclass :: parsons.TargetSmartAutomation
   :inherited-members: