*********
Utilities
*********

.. _cloud-storage:

=============
Cloud Storage
=============

The Parsons cloud storage utility was created to interact with APIs that require access to files
to run an asynchronous process.

The cloud storage utility is currently being utilitized primarily by the NGPVAN class
methods such as :func:`~parsons.ngpvan.van.Scores.upload_scores` and
:func:`~parsons.ngpvan.van.SavedLists.upload_saved_list`.

These methods have arguments specific their method, but all also contain the following cloud
storage arguments:

* ``url_type`` - The type of cloud storage to utilize. Currently ``S3`` or ``GCS``.

* ``**url_kwargs`` - These are arguments specific to the cloud storage type in order to initialize. They
  are listed below based on the url type.

The file will then be converted to a CSV, compressed and posted to the cloud storage. A presigned url will
be generated and active by default for 60 minutes, but you can adjust the time.

**Amazon S3**

Below are the required and optional arguments utilizing Amazon S3 as the cloud storage service:

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

**Google Cloud Storage**

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

.. _dbt:

=============
dbt Utilities
=============

.. autoclass:: parsons.utilities.dbt.dbt.dbtRunnerParsons
   :inherited-members:
   :members:
   
.. autofunction:: parsons.utilities.dbt.dbt.run_dbt_commands
