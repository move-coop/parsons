########
New/Mode
########

Overview
========

`New/Mode <https://www.newmode.net/>`_ is a multi-channel advocacy and civic engagement platform
for organizations and campaigns. This Parsons class includes methods for fetching tools, actions, targets, campaigns,
organizations, services, and outreaches. There are also methods for looking up targets and running actions given a
``tool_id``. Most methods return either individual items as dictionaries or lists of items as Parsons :ref:`Table` objects.

.. admonition:: Authentication

   To use the class, you need to provide a New/Mode username and password. For more information,
   see `The New/Mode API is Here <https://blog.newmode.net/new-modes-api-is-here-4c4b70c6fce6>`_.

Quickstart
==========

To instantiate the :class:`~parsons.newmode.newmode.Newmode` class, you can either store your New/Mode username
and password as environmental variables (``NEWMODE_API_USER`` and ``NEWMODE_API_PASSWORD``,
respectively) or pass in your username and password as arguments.

.. code-block:: python
   :caption: API credentials stored as environmental variables

   from parsons import Newmode
   newmode = Newmode()

.. code-block:: python
   :caption: API credentials passed as arguments

   from parsons import Newmode
   newmode = Newmode(api_user='my_username', api_password='my_password')

.. code-block:: python
   :caption: Get existing tools

   tools = newmode.get_tools()

.. code-block:: python
   :caption: Get specific tool

   tool = newmode.get_tool(tool_id)

API
====

.. autoclass:: parsons.newmode.newmode.Newmode
   :members:

.. autoclass:: parsons.newmode.newmode.NewmodeV2
   :members:
   :inherited-members:

.. autoclass:: parsons.newmode.newmode.NewmodeV1
   :members:
   :inherited-members:
