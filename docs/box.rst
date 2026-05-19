Box
=================

********
Overview
********

`Box <https://box.com>`_ is a commercial file sharing service similar to Dropbox and Google Drive. The current Parsons API supports listing files and folders, creating and deleting folders, and uploading/downloading Parsons tables as either CSV or JSON files.

.. note::

  Authentication
    This connector requires authentication credentials for a Box account. The simplest form of authentication is a through a BoxDeveloperTokenAuth, and this document will cover how to use it. Information on setting up credentials for a developer access token can be found at the `Create a Platform App page <https://developer.box.com/guides/applications/platform-apps/create>`_. On the Configuration tab, check enable "Write all files and folders stored in Box" under Application Scopes, and save, prior to generating a token. If you fail to do so, the token will not have the correct scope. Developer access tokens are not recommended for production environments. However, Box supports a variety of `authentication methods <https://github.com/box/box-python-sdk/blob/main/docs/authentication.md>`_.

**********
Quickstart
**********

This class requires credentials in the form of Box Authentication passed to the constructor, or made available as an environment variable in the form of an access token:

.. code-block:: bash

  # Note: these are fake keys, provided as examples.
  export BOX_ACCESS_TOKEN=7B39m3ozIGyTcazbWRbi5F2SSZ5J

.. note::
  Performance
    Most functions in this class exist both in 'path'-based form and 'folder_id'/'file_id'-based form. The path-based forms rely on the `get_item_id()` method, which navigates through subfolders with sequential API calls. This can be slow and computationally expensive if the Box path string in question is long, or intermediate folders contain many items. If efficiency and memory management is paramount, consider using the "by_id" methods of each function. In most cases, the id will be more accessible from returns on upload methods despite this documentation describing both methods.

**Instantiate class**

.. code-block:: python

   from parsons import Box

   # First approach: Use API credentials via environmental variables.
   box = Box()

   # Second approach: Pass API authentication as an argument.
   from box_sdk_gen import BoxDeveloperTokenAuth
   access_token = "7B39m3ozIGyTcazbWRbi5F2SSZ5J"
   oauth = BoxDeveloperTokenAuth(token=access_token)
   box = Box(auth=oauth):

**Create a subfolder and upload a Parsons table to it**

.. code-block:: python

  # Create folder inside default folder.
  my_folder_id = box.create_folder("My Folder")

  # Create subfolder inside new folder and upload table to it.
  box.create_folder(path="My Folder/My Subfolder")
  box_file = box.upload_table(table=my_parsons_table,
                              path="My Folder/My Subfolder/My Parsons Table")

  # Create new subfolder using folder_id and upload table to it.
  sub_folder_id = box.create_folder_by_id(folder_name="My SubFolder",
                                          parent_folder_id=my_folder_id)
  box_file = box.upload_table_to_folder_id(table=my_parsons_table,
                                           file_name="My Parsons Table",
                                           folder_id=sub_folder_id)

**List folders and files**

.. code-block:: python

  # List default folder.
  default_folder_list = box.list()

  # Subfolder list - by Box path str.
  subfolder_list = box.list("My Folder/My Subfolder")

  subfolder_file_list = box.list(path="My Folder/My Subfolder",
                                 item_type="file")

  # Subfolder list - by id.
  subfolder_file_list = box.list_files_by_id(folder_id="533944")
  subfolder_folder_list = box.list_folders_by_id(folder_id="533944")
  all_items = box.list_items_by_id(folder_id="533944")

**Upload tables to Box**

.. code-block:: python

  # Upload a table as a csv file.
  uploaded_table = box.upload_table(my_data_table, path="My Folder/My Subfolder/My Parsons Table", format="csv")

  # Upload a table as a json file.
  uploaded_table = box.upload_table(my_data_table, path="My Folder/My Subfolder/My Parsons Table", format="json")

**Retrieve tables from Box**

.. code-block:: python

  # Download a table (csv).
  downloaded_table = box.get_table(path="My Folder/My Subfolder/My Parsons Table", format="csv")

  # Download a table (csv) using file id.
  downloaded_table = box.get_table_by_file_id(file_id=box_file_id, format="csv")

**Upload files to Box**

.. code-block:: python

  # Upload a file to a specified location.
  uploaded_file = box.upload_file(my_file, path="My Folder/My Subfolder/My File")

**Retrieve files from Box**

.. code-block:: python

  # Download a file to a temporary file.
  downloaded_file = box.download_file("My Folder/My Subfolder/My File")

  # Download a file to a persistent, specified location.
  downloaded_file = box.download_file("My Folder/My Subfolder/My File", local_path="my_file.dat")

**Get an item id from a Box path str**

.. code-block:: python

  file_id = box.get_item_id(path="My Folder/My Subfolder/My Parsons Table")

**Delete folders/files**

.. code-block:: python

  # Delete a file.
  box.delete_file(path="My Folder/My Subfolder/My Parsons Table")
  # Delete a file by id.
  box.delete_file_by_id(file_id=file_id)

  box.delete_folder(path="My Folder/My Subfolder")
  box.delete_folder_by_id(folder_id=subfolder_id)

***
API
***

.. autoclass:: parsons.box.box.Box
   :inherited-members:
   :members:
