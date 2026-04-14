############
Google Drive
############

Overview
========

The GoogleDrive class allows you to interact with Google Drive. You can update permissions with this connector.

In order to instantiate the class, you must pass Google service account credentials as a dictionary, or store the credentials as a
JSON file locally and pass the path to the file as a string in the ``GOOGLE_DRIVE_CREDENTIALS`` environment variable. You can follow these steps:

- Go to the `Google Developer Console <https://console.cloud.google.com/apis/dashboard>`_ and make sure the "Google Drive API" is enabled.
- Go to the credentials page via the lefthand sidebar. On the credentials page, click "create credentials".
- Choose the "Service Account" option and fill out the form provided. This should generate your credentials.
- Select your newly created Service Account on the credentials main page.
- select "keys", then "add key", then "create new key". Pick the key type JSON. The credentials should start to automatically download.

You can now copy and paste the data from the key into your script or (recommended) save it locally as a JSON file.

Quickstart
==========

To instantiate the GoogleDrive class, you can either pass the constructor a dict containing your Google service account credentials
or define the environment variable ``GOOGLE_DRIVE_CREDENTIALS`` to contain a path to the JSON file containing the dict.

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import GoogleDrive
   drive = GoogleDrive()

.. code-block:: python
   :caption: Pass API credentials as argument

   from parsons import GoogleDrive
   credential_filename = 'google_drive_service_credentials.json'
   drive = GoogleDrive(app_creds=credential_filename)

.. code-block:: python
   :caption: Access Drive API methods

   new_folder = drive.create_folder(name='My Folder')

API
====

.. autoclass:: parsons.google.google_drive.GoogleDrive
   :inherited-members:
   :members:
