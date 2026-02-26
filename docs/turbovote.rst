TurboVote
=========

********
Overview
********

`TurboVote <https://turbovote.org/>`_ is an online voter registration and vote by mail
tool. This class contains a single method which allows you to export your users
(aka signups).

.. note::

  Authentication
    TurboVote requires `HTTP Basic Auth <https://en.wikipedia.org/wiki/Basic_access_authentication>`_.
    Clients with a TurboVote account must pass their username, password, and subdomain.

**********
QuickStart
**********

To instantiate the ``TurboVote`` class, you can either store your TurboVote API
username, password, subdomain as environmental variables (``TURBOVOTE_USERNAME``,
``TURBOVOTE_PASSWORD``, and ``TURBOVOTE_SUBDOMAIN``, respectively) or pass them
in as arguments:

.. code-block:: python

   from parsons import TurboVote

   # First approach: Pass credentials via environmental variables.
   tv = TurboVote()

   # Second approach: Pass credentials as arguments.
   tv = TurboVote(username='me', password='pass', subdomain='myorg')

You can then call the method:

.. code-block:: python

    # Get users
    tv.get_users()

***
API
***

.. autoclass:: parsons.turbovote.turbovote.TurboVote
   :inherited-members:
   :members:
   