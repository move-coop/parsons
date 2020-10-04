Box
=================

********
Overview
********

`Box <https://box.com>`_ is a commercial file sharing service similar to Dropbox and Google Drive. The current Parsons API supports listing files and folders, creating and deleting folders, and uploading/downloading Parsons tables as (at the moment only) CSV files.

.. note::
  Authentication
    This connector requires authentication credentials for a Box business-level account. Information on setting up those credentials can be found at the `Box Custom App Quick Start page <https://developer.box.com/guides/applications/custom-apps/oauth2-setup/>`_.

**********
Quickstart
**********

This class requires credentials in the form three strings to be either passed into the constructor or made available as environment variables:

.. code-block:: bash

  export BOX_CLIENT_ID=dp4rqi0cz5qckz361fziavdtdwxz
  export BOX_CLIENT_SECRET=4KHMDLVy89TeuUpSRa4CN5o35u9h
  export BOX_ACCESS_TOKEN=7B39m3ozIGyTcazbWRbi5F2SSZ5J


**Instantiate class**

.. code-block:: python

   from parsons import Box

   # First approach: Use API credentials via environmental variables
   box = Box()

   # Second approach: Pass API credentials as arguments
   box = Box(client_id='dp4rqi0cz5qckz361fziavdtdwxz',
             client_secret='4KHMDLVy89TeuUpSRa4CN5o35u9h',
             access_token='7B39m3ozIGyTcazbWRbi5F2SSZ5J'):

**List folders and files**

.. code-block:: python

  # List default folder
  folder_list = box.list_folders()

  # Subfolders of folder id 533944
  subfolder_list = box.list_folders(folder_id='533944')

  # List files in default folder
   file_list = box.list_files()

   # List files in a subfolder
   subfolder_file_list = box.list_files(folder_id='533944')

   all_items = box.list_items(folder_id='533944')

**Create a subfolder and upload a Parsons table to it**

.. code-block:: python

  new_folder = box.create_folder(folder_name='My Folder',
                                 parent_folder='533944')
  box_file = box.upload_file(table=my_parsons_table,
                             file_name='My Parsons Table',
                             folder_id='533944')

  downloaded_table = box.get_table(file_id=box_file.id)

  box.delete_file(box_file.id)



***
API
***

.. autoclass:: parsons.Box
   :inherited-members:
