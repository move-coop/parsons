#########
Utilities
#########

API Connector
=============

.. automodule:: parsons.utilities.api_connector
   :inherited-members:
   :members:

Check ENV
=========

.. automodule:: parsons.utilities.check_env
   :inherited-members:
   :members:

Cloud Storage
=============

The Parsons cloud storage utility was created to interact with APIs that
require access to files to run an asynchronous process.

The cloud storage utility is currently being utilitized primarily by the
NGPVAN class methods such as :meth:`~parsons.ngpvan.scores.Scores.upload_scores`
and :meth:`~parsons.ngpvan.saved_lists.SavedLists.upload_saved_list`.

These methods have arguments specific their method,
but all also contain the following cloud storage arguments:

* ``url_type`` - The type of cloud storage to utilize. Currently ``S3`` or ``GCS``.

* ``**url_kwargs`` - These are arguments specific to the cloud storage type in order to initialize.
  They are listed below based on the url type.

The file will then be converted to a CSV, compressed and posted to the cloud storage.
A presigned url willbe generated and active by default for 60 minutes,
but you can adjust the time.

.. automodule:: parsons.utilities.cloud_storage
   :inherited-members:
   :members:

Amazon S3
---------

Below are the required and optional arguments utilizing
Amazon S3 as the cloud storage service:

.. list-table::
   :widths: 25 25 100
   :header-rows: 1

   * - Argument
     - Required
     - Description
   * - ``bucket``
     - Yes
     - The S3 bucket to post the file
   * - ``aws_access_key``
     - No
     - Required if ``AWS_ACCESS_KEY_ID`` env variable not set.
   * - ``aws_secret_access_key``
     - No
     - Required if ``AWS_SECRET_ACCESS_KEY`` env variable not set.
   * - ``public_url_expires``
     - No
     - Defaults is 60 minutes.

Google Cloud Storage
--------------------

Below are the required and optional arguments utilizing Google Cloud Storage as the cloud storage service:

.. list-table::
   :widths: 25 25 100
   :header-rows: 1

   * - Argument
     - Required
     - Description
   * - ``bucket``
     - Yes
     - The S3 bucket to post the file
   * - ``app_creds``
     - No
     - Required if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable not set.
   * - ``public_url_expire``
     - No
     - Defaults is 60 minutes.

Credential Tools
================

.. automodule:: parsons.utilities.credential_tools
   :inherited-members:
   :members:

Datetime
========

.. automodule:: parsons.utilities.datetime
   :inherited-members:
   :members:

Files
=====

.. automodule:: parsons.utilities.files
   :inherited-members:
   :members:

Format Phone Number
===================

.. automodule:: parsons.utilities.format_phone_number
   :inherited-members:
   :members:

Format JSON
===========

.. automodule:: parsons.utilities.json_format
   :inherited-members:
   :members:

OAuth API Connector
===================

.. automodule:: parsons.utilities.oauth_api_connector
   :inherited-members:
   :members:

SQL Helpers
===========

.. automodule:: parsons.utilities.sql_helpers
   :inherited-members:
   :members:

SSH Utilities
=============

.. automodule:: parsons.utilities.ssh_utilities
   :inherited-members:
   :members:

ZIP Archive
===========

.. automodule:: parsons.utilities.zip_archive
   :inherited-members:
   :members:

dbt Utilities
=============

.. automodule:: parsons.utilities.dbt.dbt
   :inherited-members:
   :members:

.. automodule:: parsons.utilities.dbt.logging
   :inherited-members:
   :members:

.. automodule:: parsons.utilities.dbt.models
   :inherited-members:
   :members:
