*********
Utilities
*********

.. _cloud-storage:
=============
Cloud Storage
=============
The Parsons cloud storage utility was created to interact with APIs that require access to files
to run an asynchronous process. While this utility currently only works with ``S3``, the goal
is add functionality for additional cloud storage services in the future.

The cloud storage utility is currently being utilitized primarily by the NGPVAN class
methods such as :func:`~parsons.ngpvan.van.Scores.upload_scores` and Bulk Import methods.

These methods have arguments specific their method, but all also contain the following cloud 
storage arguments:

* ``url_type`` - The type of cloud storage to utilize. Currently only ``S3``.

* ``**url_kwargs`` - These are arguments specific to the cloud storage type in order to initialize.

**S3**

When you select the ``url_type`` S3, the Parsons table will be converted to a csv and compressed. The file will be posted to an S3 bucket. A presigned public url will be generated and returned. The url will be active by default for 60 minutes, however you may adjust that time.

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


