###########
Google Docs
###########

Overview
========

The GoogleDocs class allows you to interact with Google Docs.
You can use this connector to access and manipulate Google Docs documents programmatically.

In order to instantiate the class, you must pass Google service account credentials as a dictionary,
or store the credentials as a JSON file locally and pass the path to the file as a string in the
``GOOGLE_DRIVE_CREDENTIALS`` environment variable. You can follow these steps:

- Go to the `Google Developer Console <https://console.cloud.google.com/apis/dashboard>`__
  and make sure the "Google Docs API" and "Google Drive API" are both enabled.
- Go to the credentials page via the lefthand sidebar. On the credentials page, click "create credentials".
- Choose the "Service Account" option and fill out the form provided. This should generate your credentials.
- Select your newly created Service Account on the credentials main page.
- select "keys", then "add key", then "create new key". Pick the key type JSON.
  The credentials should start to automatically download.

You can now copy and paste the data from the key into your script
or (recommended) save it locally as a JSON file.

Quickstart
==========

Define the environment variable ``GOOGLE_DRIVE_CREDENTIALS``
to contain a path to the JSON file containing the dict.

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import GoogleDocs
   docs = GoogleDocs()

.. code-block:: python
   :caption: Pass API credentials as argument

   from parsons import GoogleDocs
   credential_filename = 'google_drive_service_credentials.json'
   docs = GoogleDocs(app_creds=credential_filename)

.. code-block:: python
   :caption: Use the client to interact with Google Docs

   # Access the Google Docs API client
   document_id = 'your-document-id'
   document = docs.client.documents().get(documentId=document_id).execute()

   # Get the document content
   content = document.get('body').get('content')

API
====

.. autoclass:: parsons.google.google_docs.GoogleDocs
   :inherited-members:
   :members:
