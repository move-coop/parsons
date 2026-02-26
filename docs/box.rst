Box
=================

********
Overview
********

`Box <https://box.com>`_ is a commercial file sharing service similar to Dropbox and Google Drive. The current Parsons API supports listing files and folders, creating and deleting folders, and uploading/downloading Parsons tables as either CSV or JSON files.

.. note::

  Authentication
    This connector requires authentication credentials for a Box business-level account. Information on setting up those credentials can be found at the `Box Custom App Quick Start page <https://developer.box.com/guides/applications/custom-apps/oauth2-setup/>`_.

**********
Quickstart
**********

This class requires credentials in the form three strings to be either passed into the constructor or made available as environment variables:

.. code-block:: bash

  # Note: these are fake keys, provided as examples.
  export BOX_CLIENT_ID=dp4rqi0cz5qckz361fziavdtdwxz
  export BOX_CLIENT_SECRET=4KHMDLVy89TeuUpSRa4CN5o35u9h
  export BOX_ACCESS_TOKEN=7B39m3ozIGyTcazbWRbi5F2SSZ5J

*NOTE*: Most functions in this class exist both in 'path'-based form and 'folder_id'/'file_id'-based form. The path-based forms rely on the `get_item_id()` method, which navigates through subfolders with sequential API calls. This can be slow and computationally expensive if the path in question is long, or intermediate folders contain many items. If efficiency is paramount, consider using the "by_id" methods of each function.

**Instantiate class**

.. code-block:: python

   from parsons import Box

   # First approach: Use API credentials via environmental variables
   box = Box()

   # Second approach: Pass API credentials as arguments
   box = Box(client_id='dp4rqi0cz5qckz361fziavdtdwxz',
             client_secret='4KHMDLVy89TeuUpSRa4CN5o35u9h',
             access_token='7B39m3ozIGyTcazbWRbi5F2SSZ5J'):

**Create a subfolder and upload a Parsons table to it**

.. code-block:: python

  # Create folder inside default folder
  my_folder_id = box.create_folder('My Folder')

  # Create subfolder inside new folder and upload table to it
  box.create_folder(path='My Folder/My Subfolder')
  box_file = box.upload_table(table=my_parsons_table,
                              path='My Folder/My Subfolder/My Parsons Table')

  # Create new subfolder using folder_id and upload table to it
  sub_folder_id = box.create_folder_by_id(folder_name='My SubFolder',
                                          parent_folder_id=my_folder_id)
  box_file = box.upload_table_to_folder_id(table=my_parsons_table,
                                           file_name='My Parsons Table',
                                           folder_id=sub_folder_id)

**List folders and files**

.. code-block:: python

  # List default folder
  default_folder_list = box.list()

  # Subfolder list - by path
  subfolder_list = box.list('My Folder/My Subfolder')

  subfolder_file_list = box.list(path='My Folder/My Subfolder',
                                 item_type='file')

  # Subfolder list - by id
  subfolder_file_list = box.list_files_by_id(folder_id='533944')
  subfolder_folder_list = box.list_folders_by_id(folder_id='533944')
  all_items = box.list_items_by_id(folder_id='533944')

**Retrieve folder/file ids from path names**

.. code-block:: python

  # Download a table
  downloaded_table = box.get_table(path='My Folder/My Subfolder/My Parsons Table')

  # Download a table using file id
  downloaded_table = box.get_table_by_file_id(file_id=box_file.id)

**Get an item id from path**

.. code-block:: python

  file_id = box.get_item_id(path='My Folder/My Subfolder/My Parsons Table')

**Delete folders/files**

.. code-block:: python

  # Delete a file
  box.delete_file(path='My Folder/My Subfolder/My Parsons Table')
  # Delete a file by id
  box.delete_file_by_id(file_id=file_id)

  box.delete_folder(path='My Folder/My Subfolder')
  box.delete_folder_by_id(folder_id=subfolder_id)

***
API
***

.. autoclass:: parsons.box.box.Box
   :inherited-members:
   :members:
   