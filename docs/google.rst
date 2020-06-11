Google
======

Google Cloud services utilize a credentials JSON file for authentication. If you are the administrator of your Google Cloud account,
you can generate them in the `Google Cloud Console APIs and Services <https://console.cloud.google.com/apis/credentials/serviceaccountkey?_ga=2.116342342.-1334320118.1565013288>`_.

********
BigQuery
********

========
Overview
========

Google BigQuery is a cloud data warehouse solution. Data is stored in tables, and users can query using SQL.
BigQuery uses datasets as top level containers for tables, and datasets are themselves contained within
Google Cloud projects.

===
API
===
.. autoclass:: parsons.GoogleBigQuery
   :inherited-members:

*************
Cloud Storage
*************

========
Overview
========
Google Cloud Storage is a cloud file storage system. It uses buckets in which to
store arbitrary files referred to as blobs.

===
API
===
.. autoclass:: parsons.GoogleCloudStorage
   :inherited-members:

*****
Civic
*****

========
Overview
========

Google Civic is an API which provides helpful information about elections. In order to access Google Civic you must
create a Google Developer Key in their `API console <https://console.developers.google.com/apis/>`_. In order to
use Google Civic, you must enable this specific end point.

The Google Civic API utilizes the `Voting Information Project <https://www.votinginfoproject.org/>`_ to collect 
key civic information such as personalized ballots and polling location information.

===
API
===

.. autoclass :: parsons.GoogleCivic
   :inherited-members:

*************
Google Sheets
*************

========
Overview
========

The GoogleSheets class allows you to interact with a Google Drive spreadsheet.

In order to instantiate the class, you must pass Google Drive credentials as a dictionary, or store the credentials as a JSON string in the ``GOOGLE_DRIVE_CREDENTIALS`` environment variable. Typically you'll get the credentials from the Google Developer Console (look for the "Google Drive API").

===
API
===

.. autoclass :: parsons.GoogleSheets
   :inherited-members:
   :members:
