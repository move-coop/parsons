TargetSmart
============

`TargetSmart <https://targetsmart.com/>`_ provides access to voter and consumer data for the progressive community. They provide
extensive services for single record lookup through their API. For larger bulk matching services
they have an automation service, which requires that data files be posted to their SFTP. Each service requires separate credentials
to utilize, which is why there are separate classes for each.

Full documentation for both services can be found at the `TargetSmart developer portal <https://docs.targetsmart.com/developers/tsapis/index.html>`_.

.. warning:: 
   Returned fields
      The fields that are returned are controlled by the TargetSmart staff. Please contact them if need any adjustments
      or alterations made to the returned fields.

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