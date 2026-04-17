##################
Azure Blob Storage
##################

Overview
========

`Azure Blob Storage <https://azure.microsoft.com/en-us/services/storage/blobs/>`_ is a cloud file storage system that
uses storage accounts to organize containers (similar to "buckets" for other storage providers) in which to store
arbitrary files referred to as 'blobs'. This Parsons integration currently only implements
`block blobs, not page or append blobs <https://docs.microsoft.com/en-us/rest/api/storageservices/understanding-block-blobs--append-blobs--and-page-blobs>`_.

.. admonition:: Authentication

   This connector requires authentication credentials for an Azure Blob Storage storage account. The
   ``azure-storage-blob`` library is used for this connector, and examples of how to create and use
   `multiple types of credentials <https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob#types-of-credentials>`_
   are included in the documentation.

Quickstart
==========

This class requires a ``credentials`` argument and *either* an ``account_name`` or an ``account_url`` argument that
includes the account name. You can store these as environmental variables (``AZURE_CREDENTIAL``, ``AZURE_ACCOUNT_NAME``,
and ``AZURE_ACCOUNT_URL``, respectively) or pass them in as arguments:

.. code-block:: python
   :caption: Use API credentials via environmental variables
   :emphasize-lines: 2

   from parsons import AzureBlobStorage
   azure_blob = AzureBlobStorage()

.. code-block:: python
   :caption: Pass API credentials as arguments
   :emphasize-lines: 2

   from parsons import AzureBlobStorage
   azure_blob = AzureBlobStorage(account_name='my_account_name', credential='1234')

.. code-block:: python
   :caption: Get all container names for a storage account

   container_names = azure_blob.list_containers()

.. code-block:: python
   :caption: Get all blob names for a storage account and container

   blob_names = azure_blob.list_blobs(container_names[0])

.. code-block:: python
   :caption: Upload a CSV file from a local file path and set the content type

   azure_blob.put_blob('blob_name', 'test1.csv', './test1.csv', content_type='text/csv')

.. code-block:: python
   :caption: Create a Table and upload it as a JSON blob

   table = Table([{'first': 'Test', 'last': 'Person'}])
   azure_blob.upload_table(table, 'blob_name', 'test2.json', data_type='json')

.. code-block:: python
   :caption: Download a blob to a temporary file path

   temp_file_path = azure_blob.download_blob('blob_name', 'test.csv')

.. code-block:: python
   :caption: Download a blob to a specific file path

   azure_blob.download_blob('blob_name', 'test.csv', local_path='/tmp/test.csv')

API
====

.. autoclass:: parsons.azure.azure_blob_storage.AzureBlobStorage
   :inherited-members:
   :members:
