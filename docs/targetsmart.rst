TargetSmart
===========

********
Overview
********

`TargetSmart <https://targetsmart.com/>`_ provides access to voter and consumer data for the progressive community.

Parsons provides two integrations with TargetSmart:

* **TargetSmart Developer API** — Methods to consume the data services provided by the TargetSmart Developer API, including low latency search and asynchronous list matching.
* **TargetSmart Automation Workflows** — Methods for interacting with TargetSmart Automation Workflows, a solution for executing custom file processing workflows programmatically. In some cases, TargetSmart will provide custom list matching solutions using Automation Workflows.

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

****************
TargetSmart API
****************

.. include:: targetsmart_api.rst
   :start-line: 7


*******************************
TargetSmart Automation Workflows
*******************************

.. include:: targetsmart_automation_workflows.rst
   :start-line: 5
