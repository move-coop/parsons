#############
Google Sheets
#############

Overview
========

The GoogleSheets class allows you to interact with Google service account spreadsheets, called "Google Sheets".
You can create, modify, read, format, share and delete sheets with this connector.

In order to instantiate the class, you must pass Google service account credentials as a dictionary,
or store the credentials as a JSON file locally and pass the path
to the file as a string in the ``GOOGLE_DRIVE_CREDENTIALS`` environment variable.

You can follow these steps:

- Go to the `Google Developer Console <https://console.cloud.google.com/apis/dashboard>`_
  and make sure the "Google Drive API" and the "Google Sheets API" are both enabled.
- Go to the credentials page via the lefthand sidebar.
  On the credentials page, click "create credentials".
- Choose the "Service Account" option and fill out the form provided.
  This should generate your credentials.
- Select your newly created Service Account on the credentials main page.
- select "keys", then "add key", then "create new key". Pick the key type JSON.
  The credentials should start to automatically download.

You can now copy and paste the data from the key into your script or (recommended) save it locally as a JSON file.

Quickstart
==========

To instantiate the GoogleSheets class, you can either pass the constructor
a dict containing your Google service account credentials
or define the environment variable ``GOOGLE_DRIVE_CREDENTIALS``
to contain a path to the JSON file containing the dict.

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import GoogleSheets
   sheets = GoogleSheets()

.. code-block:: python
   :caption: Pass API credentials as argument

   credential_filename = 'google_drive_service_credentials.json'
   credentials = json.load(open(credential_filename))
   sheets = GoogleSheets(google_keyfile_dict=credentials)

.. code-block:: python
   :caption: Create/modify/retrieve documents using instance methods

   sheet_id = sheets.create_spreadsheet('Voter Cell Phones')
   sheets.append_to_sheet(sheet_id, people_with_cell_phones)
   parsons_table = sheets.get_worksheet(sheet_id)

You may also want to share the document with your service or user account.

API
====

.. autoclass:: parsons.google.google_sheets.GoogleSheets
   :inherited-members:
   :members:
