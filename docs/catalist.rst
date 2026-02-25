Catalist
========

********
Overview
********

The CatalistMatch class allows you to interact with the Catalist M Tool (match) API. Users of this Parsons integration can use the Parsons table format to send input files to the M Tool and receive back a matched version of that table.

.. note::

  Authentication
    In order to use this class you must be provided with an OAuth Client ID and Client Secret from catalist, as well as SFTP credentials. You will also need to have Catalist whitelist the IP address you are using to access the M Tool.

==========
Quickstart
==========

To instantiate the CatalistMatch class, you must provide your ``client_id``, ``client_secret``, ``sftp_username`` and ``sftp_password`` values as arguments:

.. code-block:: sh

   # In bash, set your environment variables like so:
   $ export CATALIST_CLIENT_ID='MY_UUID'
   $ export CATALIST_CLIENT_SECRET='MY_SECRET'
   $ export CATALIST_SFTP_USERNAME='MY_USERNAME'
   $ export CATALIST_SFTP_PASSWORD='MY_PASSWORD'

.. code-block:: python

   import os
   from parsons import CatalistMatch

   match = CatalistMatch(
     client_id=os.environ['CATALIST_CLIENT_ID'],
     client_secret=os.environ['CATALIST_CLIENT_SECRET'],
     sftp_username=os.environ['CATALIST_SFTP_USERNAME'],
     sftp_password=os.environ['CATALIST_SFTP_PASSWORD']
   )

You can then load a CSV as a Parsons table and submit it for matching, then save the resulting matched Parsons table as a CSV.

.. code-block:: python

    source_table = Table.from_csv(source_filepath)
    result_table = match.match(source_table)
    result_table.to_csv(result_filepath)

***
API
***

.. autoclass:: parsons.catalist.catalist.CatalistMatch
   :inherited-members:
   :members:
   