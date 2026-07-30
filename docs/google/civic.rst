#####
Civic
#####

Overview
========

Google Civic is an API which provides helpful information about elections. In order to access Google Civic you must
create a Google Developer Key in their `API console <https://console.developers.google.com/apis/>`__. In order to
use Google Civic, you must enable this specific end point.

The Google Civic API utilizes the `Voting Information Project <https://www.votinginfoproject.org/>`__ to collect
key civic information such as personalized ballots and polling location information.

Quickstart
==========

To instantiate the GoogleCivic class, you can pass the constructor a string containing the
Google Civic API key you've generated for your project, or set the
environment variable ``GOOGLE_CIVIC_API_KEY`` to that value.

.. code-block:: python
   :caption: Set the credentials as an environment variable

   from parsons import GoogleCivic

   # May either be the file name or a JSON encoding of the credentials.
   os.environ['GOOGLE_CIVIC_API_KEY'] = 'AIzaSyAOVZVeL-snv3vNDUdw6QSiCvZRXk1xM'

   google_civic = GoogleCivic()

.. code-block:: python
   :caption: Pass the credentials in as an argument

   google_civic = GoogleCivic(api_key='AIzaSyAOVZVeL-snv3vNDUdw6QSiCvZRXk1xM')

.. code-block:: python
   :caption: Retrieve election information

   elections = google_civic.get_elections()

   address = '1600 Pennsylvania Avenue, Washington DC'
   election_id = '7000'  # General Election
   google_civic.get_polling_location(election_id=election_id, address=address)

.. code-block:: python
   :caption: Retrieve represntative information such as offices, officals, etc

   address = '1600 Pennsylvania Avenue, Washington DC'
   representatives = google_civic.get_representatives_by_address(address=address)

API
====

.. autoclass:: parsons.google.google_civic.GoogleCivic
   :inherited-members:
   :members:
