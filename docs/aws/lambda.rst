######
Lambda
######

Overview
========

Parsons' :func:`~lambda_distribute.distribute_task` function allows you to distribute process rows of a table across multiple
`AWS Lambda <https://aws.amazon.com/lambda/>`_ invocations.

If you are running the processing of a table inside AWS Lambda, then you are limited by how many rows can be processed
within the Lambda's time limit (at time-of-writing, maximum 15min).

Based on experience and some napkin math, with the same data that would allow 1000 rows to be processed inside a single
AWS Lambda instance, this method allows 10 MILLION rows to be processed.

Rather than converting the table to SQS or other options, the fastest way is to upload the table to S3, and then invoke
multiple Lambda sub-invocations, each of which can be sent a byte-range of the data in the S3 CSV file for which to process.

Using this method requires some setup. You have three tasks:

#. Define the function to process rows, the first argument, must take your table's data (though only a subset of rows will be passed) (e.g. ``def task_for_distribution(table, **kwargs):``)
#. Where you would have run ``task_for_distribution(my_table, **kwargs)`` instead call ``distribute_task(my_table, task_for_distribution, func_kwargs=kwargs)`` (either setting env var S3_TEMP_BUCKET or passing a ``bucket=`` parameter)
#. Setup your Lambda handler to include :func:`~aws_async.event_command` (or run and deploy your lambda with `Zappa <https://github.com/Miserlou/Zappa>`_)

To test locally, include the argument ``storage="local"``, which will test the :func:`~lambda_distribute.distribute_task` function, but run the task sequentially and in local memory.

Quickstart
==========

.. code-block:: python
   :caption: Minimalistic example Lambda handler

   from parsons.aws import event_command, distribute_task

   def process_table(table, foo, bar=None):
      for row in table:
         do_sloooooow_thing(row, foo, bar)

   def handler(event, context):
      ## ADD THESE TWO LINES TO TOP OF HANDLER:
      if event_command(event, context):
         return

      table = FakeDatasource.load_to_table(username='123', password='abc')

      # table is so big that running
      # process_table(table, foo=789, bar='baz')
      # would timeout so instead we:
         distribute_task(
            table, process_table,
            bucket='my-temp-s3-bucket',
            func_kwargs={'foo': 789, 'bar': 'baz'}
         )

API
====

.. autofunction:: parsons.aws.lambda_distribute.distribute_task

.. autofunction:: parsons.aws.aws_async.event_command
