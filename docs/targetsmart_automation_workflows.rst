:orphan:

TargetSmart Automation Workflows
================================

In addition to the :doc:`TargetSmart Developer API <../targetsmart_api>`,
TargetSmart also provides a solution for executing custom data processing
workflows that TargetSmart implements for specific client needs. The
``TargetSmartAutomation`` class can be used to execute these workflows for
common purposes such as customized list matching workflows.

.. note::
  Authentication
    TargetSmart Automation workflows use SFTP. You will need to obtain SFTP credentials from TargetSmart to utilize the ``TargetSmartAutomation`` class.

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
   ts_auto = TargetSmartAutomation(sftp_username='my_sftp_username', sftp_password='my_sftp_password')

You can then call these methods:

.. code-block:: python

   # Check the status of a workflow execution
   ts_auto.match_status(job_name='my_job_name')

   # Remove all files for the match job
   ts_auto.remove_files(job_name='my_job_name')

API
===

.. autoclass :: parsons.TargetSmartAutomation
   :inherited-members:
