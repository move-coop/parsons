################################
TargetSmart Automation Workflows
################################

In addition to the :doc:`TargetSmart Developer API <../targetsmart_api>`,
TargetSmart also provides a solution for executing custom data processing
workflows that TargetSmart implements for specific client needs. The
:class:`~parsons.targetsmart.targetsmart_automation.TargetSmartAutomation`
class can be used to execute these workflows for common purposes such
as customized list matching workflows. Workflow execution can take minutes
to hours depending on the workflow type, size of data, and queuing.

.. admonition:: Authentication

   TargetSmart Automation workflows use SFTP.
   You will need to obtain SFTP credentials from TargetSmart to utilize
   :class:`~parsons.targetsmart.targetsmart_automation.TargetSmartAutomation`.

Quickstart
==========

To instantiate :class:`~parsons.targetsmart.targetsmart_automation.TargetSmartAutomation`,
you can either store your SFTP username and password as the environmental variables
``TS_SFTP_USERNAME`` and ``TS_SFTP_PASSWORD``, or pass them in as
keyword arguments. Credentials for your account are provided by TargetSmart.

.. code-block:: python
   :caption: Store SFTP username and password as environmental variables

   from parsons import TargetSmartAutomation
   ts_auto = TargetSmartAutomation()

.. code-block:: python
   :caption: Pass SFTP username and password as arguments
   :emphasize-lines: 3-5

   # DO NOT store password literals in your source code.
   from parsons import TargetSmartAutomation
   ts_auto = TargetSmartAutomation(
       sftp_username='my_sftp_username', sftp_password='my_sftp_password'
   )

You can then call class methods:

.. code-block:: python

   input_table = Table.from_csv('my_file_to_match.csv')

   # Execute a custom workflow that TargetSmart has provisioned for you. This
   # blocks until completion and may take minutes/hours depending on the data size
   # and workflow type
   output_table = ts_auto.match(
       input_table,
       'workflow_name_provided_by_targetsmart',
       'my_job_name',
       emails=['bob@example.com'],
   )

   # Most Automation workflows perform list matching, but not all.
   # The :meth:`~TargetSmartAutomation.execute` method is an alias for the
   # :meth:`~TargetSmartAutomation.match` method to avoid confusion in these cases.
   # This is the equivalent to the above
   output_table = ts_auto.execute(
       input_table,
       'workflow_name_provided_by_targetsmart',
       'my_job_name',
       emails=['bob@example.com'],
   )

   # Optionally check the status of a workflow execution
   ts_auto.match_status(job_name='my_job_name')

   # Optionally remove all files for the match job. TargetSmart's lifecycle rules
   # will remove eventually if not.
   ts_auto.remove_files(job_name='my_job_name')

API
====

.. autoclass:: parsons.targetsmart.targetsmart_automation.TargetSmartAutomation
   :inherited-members:
   :members:
