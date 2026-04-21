#############
Cloud Storage
#############

Overview
========
Google Cloud Storage is a cloud file storage system. It uses buckets in which to
store arbitrary files referred to as blobs. You may use this connector to upload
Parsons tables as blobs, download them to files, and list available blobs.

To use the GoogleCloudStorage class, you will need Google service account credentials.
If you are the administrator of your Google Cloud account, you can generate them at
`Service accounts - IAM & Admin <https://console.cloud.google.com/projectselector2/iam-admin/serviceaccounts>`__
Once signed in, select your project, then your project's email, then Keys,
then ``Add key``, and finally ``Create new key``.

Quickstart
==========

To instantiate the GoogleBigQuery class, you can pass the constructor a string containing
either the name of your Google service account credentials file or a JSON string
encoding those credentials. Alternatively, you can set the environment variable
``GOOGLE_APPLICATION_CREDENTIALS`` to be either of those strings and
call the constructor without that argument.

.. code-block:: python
   :caption: Set the credentials as an environment variable

   from parsons import GoogleCloudStorage

   # May be the file name or a JSON encoding of the credentials.
   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_credentials_file.json'

   gcs = GoogleCloudStorage()

.. code-block:: python
   :caption: Pass the credentials in as an argument

   credentials_filename = 'google_credentials_file.json'
   project = 'parsons-test'    # Project in which we're working
   gcs = GoogleCloudStorage(app_creds=credentials_filename, project=project)

.. code-block:: python
   :caption: create buckets, upload blobs to them, and list/retrieve the available blobs

   gcs.create_bucket('parsons_bucket')
   gcs.list_buckets()

   gcs.upload_table(bucket='parsons_bucket', table=parsons_table, blob_name='parsons_blob')
   gcs.get_blob(bucket_name='parsons_bucket', blob_name='parsons_blob')

API
====

.. autoclass:: parsons.google.google_cloud_storage.GoogleCloudStorage
   :inherited-members:
   :members:
