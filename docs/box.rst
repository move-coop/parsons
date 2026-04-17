####
Box
####

Overview
========

`Box <https://box.com>`__ is a commercial file sharing service similar to Dropbox and Google Drive.
The current Parsons API supports listing files and folders, creating and deleting folders,
and uploading/downloading Parsons tables as either CSV or JSON files.

.. admonition:: Authentication

   This connector requires authentication credentials for a Box account.
   The simplest form of authentication is a through a BoxDeveloperTokenAuth, and this document will cover how to use it.
   Information on setting up credentials for a developer access token can be found at the
   `Create a Platform App page <https://developer.box.com/guides/applications/platform-apps/create>`__.
   On the Configuration tab, check enable "Write all files and folders stored in Box"
   under Application Scopes, and save, prior to generating a token.
   If you fail to do so, the token will not have the correct scope.
   Developer access tokens are not recommended for production environments.
   However, Box supports a variety of `authentication methods <https://github.com/box/box-python-sdk/blob/main/docs/authentication.md>`__.

Quickstart
==========

This class requires credentials in the form of Box Authentication passed to the constructor,
or made available as an environment variable in the form of an access token:

.. code-block:: bash

   # Note: these are fake keys, provided as examples.
   export BOX_ACCESS_TOKEN=7B39m3ozIGyTcazbWRbi5F2SSZ5J

.. admonition:: Performance

   Most functions in this class exist both in 'path'-based form and 'folder_id'/'file_id'-based form.
   The path-based forms rely on the :meth:`~parsons.box.box.Box.get_item_id` method, which navigates through subfolders with sequential API calls.
   This can be slow and computationally expensive if the Box path string in question is long, or intermediate folders contain many items.
   If efficiency and memory management is paramount, consider using the "by_id" methods of each function.
   In most cases, the id will be more accessible from returns on upload methods despite this documentation describing both methods.

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import Box
   box = Box()

.. code-block:: python
   :caption: Pass API authentication as an argument
   :emphasize-lines: 3-5

   from parsons import Box
   from box_sdk_gen import BoxDeveloperTokenAuth
   access_token = "7B39m3ozIGyTcazbWRbi5F2SSZ5J"
   oauth = BoxDeveloperTokenAuth(token=access_token)
   box = Box(auth=oauth):

.. code-block:: python
   :caption: Create folder inside default box folder

   my_folder_id = box.create_folder("My Folder")

.. code-block:: python
   :caption: Create subfolder inside new folder and upload table to it

   box.create_folder(path="My Folder/My Subfolder")
   box_file = box.upload_table(table=my_parsons_table,
   path="My Folder/My Subfolder/My Parsons Table")

.. code-block:: python
   :caption: Create new subfolder using folder_id and upload table to it

   sub_folder_id = box.create_folder_by_id(
      folder_name="My SubFolder",
      parent_folder_id=my_folder_id,
   )
   box_file = box.upload_table_to_folder_id(
      table=my_parsons_table,
      file_name="My Parsons Table",
      folder_id=sub_folder_id,
   )

.. code-block:: python
   :caption: List default folder

   default_folder_list = box.list()

.. code-block:: python
   :caption: Get subfolder list - by Box path string

   subfolder_list = box.list("My Folder/My Subfolder")

   subfolder_file_list = box.list(
       path="My Folder/My Subfolder",
       item_type="file",
   )

.. code-block:: python
   :caption: Get subfolder list - by Box ID

   subfolder_file_list = box.list_files_by_id(folder_id="533944")
   subfolder_folder_list = box.list_folders_by_id(folder_id="533944")
   all_items = box.list_items_by_id(folder_id="533944")

.. code-block:: python
   :caption: Upload tables to Box as a csv file

   uploaded_table = box.upload_table(my_data_table, path="My Folder/My Subfolder/My Parsons Table", format="csv")

.. code-block:: python
   :caption: Upload tables to Box as a json file

   uploaded_table = box.upload_table(my_data_table, path="My Folder/My Subfolder/My Parsons Table", format="json")

.. code-block:: python
   :caption: Retrieve tables from a csv in Box using Box path

   downloaded_table = box.get_table(path="My Folder/My Subfolder/My Parsons Table", format="csv")

.. code-block:: python
   :caption: Retrieve tables from a csv in Box using file ID

   downloaded_table = box.get_table_by_file_id(file_id=box_file_id, format="csv")

.. code-block:: python
   :caption: Upload files to specific location in Box using Box path

   uploaded_file = box.upload_file(my_file, path="My Folder/My Subfolder/My File")

.. code-block:: python
   :caption: Download a file from Box to a temporary local file

   downloaded_file = box.download_file("My Folder/My Subfolder/My File")

.. code-block:: python
   :caption: Download a file from Box to a specific local path

   downloaded_file = box.download_file("My Folder/My Subfolder/My File", local_path="my_file.dat")

.. code-block:: python
   :caption: Get an item id from a Box path str

   file_id = box.get_item_id(path="My Folder/My Subfolder/My Parsons Table")

.. code-block:: python
   :caption: Delete folders/files

   box.delete_file(path="My Folder/My Subfolder/My Parsons Table")

   box.delete_file_by_id(file_id=file_id)

   box.delete_folder(path="My Folder/My Subfolder")

   box.delete_folder_by_id(folder_id=subfolder_id)

API
====

.. autoclass:: parsons.box.box.Box
   :inherited-members:
   :members:
