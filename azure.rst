Azure
=====

************
Blob Storage
************

========
Overview
========
Azure Blob Storage is a cloud file storage system. It uses storage accounts to organize containers (similar to
"buckets" for other storage providers) in which to store arbitrary files referred to as blobs.

This connector currently only implements block blobs and not page or append blobs.

You'll need credentials for an Azure Blob Storage storage account to use this connector. The ``azure-storage-blob``
library is used for this connector, and `examples of how to create and use multiple types of credentials
<https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob#types-of-credentials>`_
are included in the documentation.

==========
Quickstart
==========

**List containers and blobs**

.. code-block:: python

  from parsons import AzureBlobStorage

  azure_blob = AzureBlobStorage()

  # Get all container names for a storage account
  container_names = azure_blob.list_containers()

  # Get all blob names for a storage account and container
  blob_names = azure_blob.list_blobs(container_names[0])


**Create a blob from a file or ``Table``**

.. code-block:: python

  from parsons import AzureBlobStorage, Table

  azure_blob = AzureBlobStorage()

  container_name = 'testcontainer'

  # Upload a CSV file from a local file path and set the content type
  azure_blob.put_blob(container_name, 'test1.csv', './test1.csv', content_type='text/csv')

  # Create a Table and upload it as a JSON blob
  table = Table([{'first': 'Test', 'last': 'Person'}])
  azure_blob.upload_table(table, container_name, 'test2.json', data_type='json')


**Download a blob**

.. code-block:: python

  from parsons import AzureBlobStorage

  azure_blob = AzureBlobStorage()

  container_name = 'testcontainer'

  # Download to a temporary file path
  temp_file_path = azure_blob.download_blob(container_name, 'test.csv')

  # Download to a specific file path
  azure_blob.download_blob(container_name, 'test.csv', local_path='/tmp/test.csv')


===
API
===
.. autoclass:: parsons.AzureBlobStorage
   :inherited-members:
