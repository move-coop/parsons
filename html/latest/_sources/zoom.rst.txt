Zoom
====

********
Overview
********

`Zoom <https://zoom.us>`_ is a video conferencing platform. This connector supports
fetching users, fetching meetings, fetching metadata for past meetings, and fetching
participants of past meetings via the `Zoom API <https://marketplace.zoom.us/docs/api-reference/zoom-api/>`_.

.. note::
  Authentication
    The ``Zoom`` class supports `JSON Web Token Authentication <https://marketplace.zoom.us/docs/guides/auth/jwt>`_.
    You must `Create a JWT App <https://marketplace.zoom.us/docs/guides/build/jwt-app>`_ to obtain
    an API Key and API Secret for authentication.

***********
Quick Start
***********

To instantiate the ``Zoom`` class, you can either store your Zoom API
key and secret as environmental variables (``ZOOM_API_KEY`` and ``ZOOM_API_SECRET``,
respectively) or pass them in as arguments:

.. code-block:: python

  from parsons import Zoom

  # If environmental variables ZOOM_API_KEY and ZOOM_API_SECRET
  # are set, no need for arguments
  zoom = Zoom()

  # If providing authentication credentials via arguments
  zoom = Zoom(api_key='my_api_key', api_secret='my_api_secret')

  # Get a table of host's meetings via their email or user id
  meetings_tbl = zoom.get_meetings('my_name@mail.com')

  # Get the list of participants in a past meeting
  participants_tbl = zoom.get_past_meeting_participants('my_meeting_id')

***
API
***

.. autoclass :: parsons.Zoom
   :inherited-members:
