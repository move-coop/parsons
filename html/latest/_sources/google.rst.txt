Google
======

Google Cloud services allow you to upload and manipulate Tables as spreadsheets (via GoogleSheets) or query them as SQL database tables (via GoogleBigQuery). You can also upload/store/download them as binary objects (via GoogleCloudStorage). Google also offers an API for civic information using GoogleCivic and admin information using the Google Workspace Admin SDK.

For all of these services you will need to enable the APIs for your Google Cloud account and obtain authentication tokens or other credentials to access them from your scripts. If you are the administrator of your Google Cloud account, you can do both of these at `Google Cloud Console APIs and Services <https://console.cloud.google.com/apis/dashboard>`_. The connectors below have more specific information about how to authenticate.

.. _gbq:

*************
Google Admin
*************

========
Overview
========

The GoogleAdmin class allows you to get information about groups and members in Google Admin.

In order to instantiate the class, you must pass Google service account credentials as a dictionary, or store the credentials as a JSON string in the ``GOOGLE_APPLICATION_CREDENTIALS`` environment variable. You must also provide an email address for `domain-wide delegation <https://developers.google.com/admin-sdk/directory/v1/guides/delegation>`_.

==========
Quickstart
==========

To instantiate the GoogleAdmin class, you can either pass the constructor a dict containing your Google service account credentials or define the environment variable ``GOOGLE_APPLICATION_CREDENTIALS`` to contain a JSON encoding of the dict.

.. code-block:: python

   from parsons import GoogleAdmin

   # First approach: Use API credentials via environmental variables
   admin = GoogleAdmin(None, 'fakeemail@fakedomain.com')

   # Second approach: Pass API credentials as argument
   credential_filename = 'google_application_credentials.json'
   credentials = json.load(open(credential_filename))
   sheets = GoogleSheets(credentials, 'fakeemail@fakedomain.com')

You can then get information about groups and members using instance methods:

.. code-block:: python

   members = admin.get_all_group_members('group_key')
   groups = admin.get_all_groups(domain='fakedomain.com')

===
API
===

.. autoclass:: parsons.google.google_admin.GoogleAdmin
   :inherited-members:


********
BigQuery
********

========
Overview
========

Google BigQuery is a cloud data warehouse solution. Data is stored in tables, and users can query using SQL.
BigQuery uses datasets as top level containers for tables, and datasets are themselves contained within
Google Cloud projects.

==========
Quickstart
==========

To instantiate the `GoogleBigQuery` class, you can pass the constructor a string containing either the name of the Google service account credentials file or a JSON string encoding those credentials. Alternatively, you can set the environment variable ``GOOGLE_APPLICATION_CREDENTIALS`` to be either of those strings and call the constructor without that argument.

.. code-block:: python

   from parsons import GoogleBigQuery

   # Set as environment variable so we don't have to pass it in. May either
   # be the file name or a JSON encoding of the credentials.
   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_credentials_file.json'

   bigquery = GoogleBigQuery()

Alternatively, you can pass the credentials in as an argument. In the example below, we also specify the project.

.. code-block:: python

   # Project in which we're working
   project = 'parsons-test'
   bigquery = GoogleBigQuery(
      app_creds='google_credentials_file.json',
      project=project
   )

We can now upload/query data.

.. code-block:: python

   dataset = 'parsons_dataset'
   table = 'parsons_table'

   # Table name should be project.dataset.table, or dataset.table, if
   # working with the default project
   table_name = f"`{project}.{dataset}.{table}`"

   # Must be pre-existing bucket. Create via GoogleCloudStorage() or
   # at https://console.cloud.google.com/storage/create-bucket. May be
   # omitted if the name of the bucket is specified in environment
   # variable GCS_TEMP_BUCKET.
   gcs_temp_bucket = 'parsons_bucket'

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
      tmp_gcs_bucket=gcs_temp_bucket
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

===
API
===
.. autoclass:: parsons.google.google_bigquery.GoogleBigQuery
   :inherited-members:


*************
Cloud Storage
*************

========
Overview
========
Google Cloud Storage is a cloud file storage system. It uses buckets in which to
store arbitrary files referred to as blobs. You may use this connector to upload Parsons tables as blobs, download them to files, and list available blobs.

To use the GoogleCloudStorage class, you will need Google service account credentials. If you are the administrator of your Google Cloud account, you can generate them in the `Google Cloud Console APIs and Services <https://console.cloud.google.com/apis/credentials/serviceaccountkey?_ga=2.116342342.-1334320118.1565013288>`_.

==========
Quickstart
==========

To instantiate the GoogleBigQuery class, you can pass the constructor a string containing either the name of your Google service account credentials file or a JSON string encoding those credentials. Alternatively, you can set the environment variable ``GOOGLE_APPLICATION_CREDENTIALS`` to be either of those strings and call the constructor without that argument.

.. code-block:: python

   from parsons import GoogleCloudStorage

   # Set as environment variable so we don't have to pass it in. May either
   # be the file name or a JSON encoding of the credentials.
   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_credentials_file.json'

   gcs = GoogleCloudStorage()

Alternatively, you can pass the credentials in as an argument. In the example below, we also specify the project.

.. code-block:: python

   credentials_filename = 'google_credentials_file.json'
   project = 'parsons-test'    # Project in which we're working
   gcs = GoogleCloudStorage(app_creds=credentials_filename, project=project)

Now we can create buckets, upload blobs to them and and list/retrieve
the available blobs.

.. code-block:: python

   gcs.create_bucket('parsons_bucket')
   gcs.list_buckets()

   gcs.upload_table(bucket='parsons_bucket', table=parsons_table, blob_name='parsons_blob')
   gcs.get_blob(bucket_name='parsons_bucket', blob_name='parsons_blob')

===
API
===
.. autoclass:: parsons.google.google_cloud_storage.GoogleCloudStorage
   :inherited-members:


*****
Civic
*****

========
Overview
========

Google Civic is an API which provides helpful information about elections. In order to access Google Civic you must
create a Google Developer Key in their `API console <https://console.developers.google.com/apis/>`_. In order to
use Google Civic, you must enable this specific end point.

The Google Civic API utilizes the `Voting Information Project <https://www.votinginfoproject.org/>`_ to collect
key civic information such as personalized ballots and polling location information.


==========
Quickstart
==========

To instantiate the GoogleCivic class, you can pass the constructor a string containing the Google Civic API key you've generated for your project, or set the environment variable ``GOOGLE_CIVIC_API_KEY`` to that value.

.. code-block:: python

   from parsons import GoogleCivic

   # Set as environment variable so we don't have to pass it in. May either
   # be the file name or a JSON encoding of the credentials.
   os.environ['GOOGLE_CIVIC_API_KEY'] = 'AIzaSyAOVZVeL-snv3vNDUdw6QSiCvZRXk1xM'

   google_civic = GoogleCivic()

Alternatively, you can pass the credentials in as an argument. In the example below, we also specify the project.

.. code-block:: python

   google_civic = GoogleCivic(api_key='AIzaSyAOVZVeL-snv3vNDUdw6QSiCvZRXk1xM')

Now you can retrieve election information

.. code-block:: python

   elections = google_civic.get_elections()

   address = '1600 Pennsylvania Avenue, Washington DC'
   election_id = '7000'  # General Election
   google_civic.get_polling_location(election_id=election_id, address=address)

You can also retrieve represntative information such as offices, officals, etc.

.. code-block:: python

   address = '1600 Pennsylvania Avenue, Washington DC'
   representatives = google_civic.get_representatives_by_address(address=address)

===
API
===

.. autoclass :: parsons.google.google_civic.GoogleCivic
   :inherited-members:


*************
Google Sheets
*************

========
Overview
========

The GoogleSheets class allows you to interact with Google service account spreadsheets, called "Google Sheets." You can create, modify, read, format, share and delete sheets with this connector.

In order to instantiate the class, you must pass Google service account credentials as a dictionary, or store the credentials as a JSON file locally and pass the path to the file as a string in the ``GOOGLE_DRIVE_CREDENTIALS`` environment variable. You can follow these steps:

- Go to the `Google Developer Console <https://console.cloud.google.com/apis/dashboard>`_ and make sure the "Google Drive API" and the "Google Sheets API" are both enabled.
- Go to the credentials page via the lefthand sidebar. On the credentials page, click "create credentials".
- Choose the "Service Account" option and fill out the form provided. This should generate your credentials.
- Select your newly created Service Account on the credentials main page.
- select "keys", then "add key", then "create new key". Pick the key type JSON. The credentials should start to automatically download.

You can now copy and paste the data from the key into your script or (recommended) save it locally as a JSON file.

==========
Quickstart
==========

To instantiate the GoogleSheets class, you can either pass the constructor a dict containing your Google service account credentials or define the environment variable ``GOOGLE_DRIVE_CREDENTIALS`` to contain a path to the JSON file containing the dict.

.. code-block:: python

   from parsons import GoogleSheets

   # First approach: Use API credentials via environmental variables
   sheets = GoogleSheets()

   # Second approach: Pass API credentials as argument
   credential_filename = 'google_drive_service_credentials.json'
   credentials = json.load(open(credential_filename))
   sheets = GoogleSheets(google_keyfile_dict=credentials)

You can then create/modify/retrieve documents using instance methods:

.. code-block:: python

   sheet_id = sheets.create_spreadsheet('Voter Cell Phones')
   sheets.append_to_sheet(sheet_id, people_with_cell_phones)
   parsons_table = sheets.get_worksheet(sheet_id)

You may also want to share the document with your service or user account.

===
API
===

.. autoclass:: parsons.google.google_sheets.GoogleSheets
   :inherited-members:

