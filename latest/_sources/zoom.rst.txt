Zoom
====

********
Overview
********

`Zoom <https://zoom.us>`_ is a video conferencing platform. This connector supports
fetching users, fetching meetings, fetching metadata for past meetings, and fetching
participants of past meetings via the `Zoom API <https://developers.zoom.us/docs/api/>`_.

.. note::

  Authentication
    The ``Zoom`` class uses server-to-server `Zoom Server-to-Server OAuth <https://developers.zoom.us/docs/internal-apps/s2s-oauth/>`_
    to authenticate queries to the Zoom API. You must create a server-to-server application at
    `Zoom App Marketplace - Create App <https://marketplace.zoom.us/develop/create>`_ to obtain an
    ``account_id``, ``client_id``, and ``client_secret`` key. You will use this OAuth application to define your scopes,
    which gives your ``Zoom`` connector read permission on endpoints of your choosing (`meetings`, `webinars`, `reports`, etc.)

***********
Quick Start
***********

To instantiate the ``Zoom`` class, you can either store your Zoom account ID, client ID, and client secret
as environmental variables (``ZOOM_ACCOUNT_ID``, ``ZOOM_CLIENT_ID``, ``ZOOM_CLIENT_SECRET``)
or pass them in as arguments.

.. code-block:: python

  from parsons import Zoom

  # If environmental variables ZOOM_API_KEY and ZOOM_API_SECRET
  # are set, no need for arguments
  zoom = Zoom()

  # If providing authentication credentials via arguments
  zoom = Zoom(
    account_id="my_account_id",
    client_id="my_client_id",
    client_secret="my_client_secret"
  )

  # Get a table of host's meetings via their email or user id
  meetings_tbl = zoom.get_meetings('my_name@mail.com')

  # Get the list of participants in a past meeting
  participants_tbl = zoom.get_past_meeting_participants('my_meeting_id')

***
API
***

.. autoclass:: parsons.zoom.zoom.Zoom
   :inherited-members:
   :members:
   