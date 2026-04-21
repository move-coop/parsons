######
Google
######

Google Cloud services allow you to upload and manipulate Tables as spreadsheets (via GoogleSheets)
or query them as SQL database tables (via GoogleBigQuery).
You can also upload/store/download them as binary objects (via GoogleCloudStorage).
Google also offers an API for civic information using GoogleCivic and admin information
using the Google Workspace Admin SDK.

For all of these services you will need to enable the APIs for your Google Cloud account and
obtain authentication tokens or other credentials to access them from your scripts.
If you are the administrator of your Google Cloud account, you can do both of these at
`Google Cloud Console APIs and Services - Dashboard <https://console.cloud.google.com/apis/dashboard>`__.
The connectors below have more specific information about how to authenticate.

.. toctree::
   :name: notifications

   admin
   bigquery
   civic
   cloud_storage
   docs
   drive
   sheets
