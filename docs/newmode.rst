New/Mode
==========

********
Overview
********

`New/Mode <https://www.newmode.net/>`_ is a multi-channel advocacy and civic engagement platform
for organizations and campaigns. This Parsons class includes methods for fetching tools, actions, targets, campaigns,
organizations, services, and outreaches. There are also methods for looking up targets and running actions given a
``tool_id``. Most methods return either individual items as dictionaries or lists of items as Parsons ``Table`` objects.

.. note::

   Authentication
      To use the class, you need to provide a New/Mode username and password. For more information,
      see `The New/Mode API is Here <https://blog.newmode.net/new-modes-api-is-here-4c4b70c6fce6>`_.

***********
Quick Start
***********

To instantiate the ``Newmode`` class, you can either store your New/Mode username
and password as environmental variables (``NEWMODE_API_USER`` and ``NEWMODE_API_PASSWORD``,
respectively) or pass in your username and password as arguments:

.. code-block:: python

    from parsons import Newmode

    # instantiate with API credentials stored as environmental variables
    newmode = Newmode()

    # instantiate with API credentials passed as arguments
    newmode = Newmode(api_user='my_username', api_password='my_password')

    # Get existing tools.
    tools = newmode.get_tools()

    # Get specific tool.
    tool = newmode.get_tool(tool_id)

***
API
***

.. autoclass:: parsons.newmode.newmode.Newmode
   :members:

.. autoclass:: parsons.newmode.newmode.NewmodeV2
   :members:
   :inherited-members:

.. autoclass:: parsons.newmode.newmode.NewmodeV1
   :members:
   :inherited-members:
