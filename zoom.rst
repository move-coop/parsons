Zoom
====

********
Overview
********

`Zoom <https://zoom.us>`_ is a video conferencing platform.

***********
Quick Start
***********

**Get Meeting Participants**

.. code-block:: python

  from parsons import Zoom
  zoom = Zoom()

  # Get a table of host's meeting's via their email or user id.
  mtgs_tbl = zoom.get_meetings(bob@bob.com) 

  # Get the list of participants in a past meeting
  par_tbl = zoom.get_past_meeting_participants('asdf123ads')

***
API
***

.. autoclass :: parsons.Zoom
   :inherited-members: