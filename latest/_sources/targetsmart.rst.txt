TargetSmart
===========

Overview
********

`TargetSmart <https://targetsmart.com/>`_ provides access to voter and consumer data for the progressive community.

TargetSmart Developer API
-------------------------

Parsons provides methods to consume the data services provided by the
TargetSmart Developer API. These services include both low latency search and asynchronous list matching.

* :doc:`Interacting with the TargetSmart Developer API <../targetsmart_api>`

TargetSmart Automation Workflows
--------------------------------

Parsons provides methods for interacting with TargetSmart Automation Workflows,
a solution for executing custom file processing workflows programmatically. In
some cases, TargetSmart will provide custom list matching solutions using
Automation Workflows.

* :doc:`Interacting with TargetSmart Automation Workflows <../targetsmart_automation_workflows>`

.. note::

  **TargetSmart Developer API versus Automation**

    Unless TargetSmart has provided a custom workflow solution for you, you can
    ignore the Automation information.

    TargetSmart's Developer API provides an HTTP-based interface for consuming the
    general web services that TargetSmart provides. The TargetSmart Automation
    system solely provides a solution for consuming customized file processing
    workflows that are provisioned for specific client needs. TargetSmart Automation
    is based on SFTP instead of HTTP.

    - `TargetSmart Developer API docs on docs.targetsmart.com  <https://docs.targetsmart.com/developers/tsapis/v2/index.html>`_
    - `TargetSmart Automation docs on docs.targetsmart.com <https://docs.targetsmart.com/my_tsmart/automation/overview.html>`_
