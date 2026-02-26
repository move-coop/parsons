Airmeet
=======

********
Overview
********

`Airmeet <https://www.airmeet.com/>`_ is a webinar platform. This connector supports
fetching events ("Airmeets"), sessions, participants, and other event data via the
`Airmeet Public API for Event Details <https://help.airmeet.com/support/solutions/articles/82000909768-1-event-details-airmeet-public-api>`_.

.. note::

  Authentication
    You must create an Access Key and Secret Key via the Airmeet website. These are used by the ``Airmeet`` class to fetch
    an access token which is used for subsequent interactions with the API. There are three region-based API endpoints; see
    the `Airmeet API documentation <https://help.airmeet.com/support/solutions/articles/82000909768-1-event-details-airmeet-public-api#3.-Authentication%C2%A0>`_ for details.

***********
Quick Start
***********

To instantiate the ``Airmeet`` class, you can either store your API endpoint, access key, and secret key as environmental
variables (``AIRMEET_URI``, ``AIRMEET_ACCESS_KEY``, ``AIRMEET_SECRET_KEY``) or pass them in as arguments.

.. code-block:: python

  from parsons import Airmeet

  # First approach: Use API credentials via environmental variables
  airmeet = Airmeet()

  # Second approach: Pass API credentials as arguments (airmeet_uri is optional)
  airmeet = Airmeet(
    airmeet_uri='https://api-gateway.airmeet.com/prod',
    airmeet_access_key="my_access_key",
    airmeet_secret_key="my_secret_key
  )

You can then call various endpoints:

.. code-block:: python

  # Fetch the list of Airmeets.
  events_tbl = airmeet.list_airmeets()

  # Fetch the list of sessions in an Airmeet.
  sessions_tbl = airmeet.fetch_airmeet_sessions("my_airmeet_id")

  # Fetch the list of registrations for an Airmeet, sorted in order
  # of registration date.
  participants_tbl = airmeet.fetch_airmeet_participants(
    "my_airmeet_id", sorting_direction="ASC"
  )

  # Fetch the list of session attendees.
  session_attendees_tbl = airmeet.fetch_session_attendance("my_session_id")

***
API
***

.. autoclass:: parsons.airmeet.airmeet.Airmeet
   :inherited-members:
   :members:
   