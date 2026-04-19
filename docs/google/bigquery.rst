########
BigQuery
########

Overview
========

Google BigQuery is a cloud data warehouse solution. Data is stored in tables, and users can query using SQL.
BigQuery uses datasets as top level containers for tables, and datasets are themselves contained within
Google Cloud projects.

Quickstart
==========

To instantiate the :class:`~parsons.google.google_bigquery.GoogleBigQuery` class, you can pass the constructor a string containing either the name of the Google service account credentials file or a JSON string encoding those credentials. Alternatively, you can set the environment variable ``GOOGLE_APPLICATION_CREDENTIALS`` to be either of those strings and call the constructor without that argument.

.. code-block:: python
   :caption: Set as environment variable

   from parsons import GoogleBigQuery

   # May either be the file name or a JSON encoding of the credentials.
   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_credentials_file.json'

   bigquery = GoogleBigQuery()

.. code-block:: python
   :caption: Pass the credentials in as an argument

   # Project in which we're working
   project = 'parsons-test'
   bigquery = GoogleBigQuery(
      app_creds='google_credentials_file.json',
      project=project
   )

.. code-block:: python
   :caption: Upload/query data

   dataset = 'parsons_dataset'
   table = 'parsons_table'

   # Table name should be project.dataset.table, or dataset.table, if
   # working with the default project
   table_name = f"`{project}.{dataset}.{table}`"

   # Must be pre-existing bucket. Create via GoogleCloudStorage() or
   # at https://console.cloud.google.com/storage/create-bucket. May be
   # omitted if the name of the bucket is specified in environment
   # variable GCS_TEMP_BUCKET.
   tmp_gcs_bucket = 'parsons_bucket'

   # Create dataset if it doesn't already exist
   bigquery.client.create_dataset(dataset=dataset, exists_ok=True)

   parsons_table = Table([{'name':'Bob', 'party':'D'},
                          {'name':'Jane', 'party':'D'},
                          {'name':'Sue', 'party':'R'},
                          {'name':'Bill', 'party':'I'}])

   # Copy table in to create new BigQuery table
   bigquery.copy(
      table_obj=parsons_table,
      table_name=table_name,
      tmp_gcs_bucket=tmp_gcs_bucket
   )

   # Select from project.dataset.table
   bigquery.query(f'select name from {table_name} where party = "D"')

   # Query with parameters
   bigquery.query(
      f"select name from {table_name} where party = %s",
      parameters=["D"]
   )

   # Delete the table when we're done
   bigquery.client.delete_table(table=table_name)

API
====

.. autoclass:: parsons.google.google_bigquery.GoogleBigQuery
   :inherited-members:
   :members:

.. _bigquery transactions documentation: https://docs.cloud.google.com/bigquery/docs/transactions
