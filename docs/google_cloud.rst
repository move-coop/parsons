Google Cloud
============

Google Cloud services utilize a credentials JSON file for authentication. If you are the administrator of your Google Cloud account,
you can generate them in the `Google Cloud Console APIs and Services <https://console.cloud.google.com/apis/credentials/serviceaccountkey?_ga=2.116342342.-1334320118.1565013288>`_.

====================
Google Cloud Storage
====================
Google Cloud Storage is a cloud file storage system. It uses buckets in which to
store arbitrary files referred to as blobs.


.. autoclass:: parsons.GoogleCloudStorage
   :inherited-members:

===============
Google BigQuery
===============
Google BigQuery is a cloud data warehouse solution. Data is stored in tables, and users can query using SQL.
BigQuery uses datasets as top level containers for tables, and datasets are themselves contained within
Google Cloud projects.

.. autoclass:: parsons.GoogleBigQuery
   :inherited-members:
