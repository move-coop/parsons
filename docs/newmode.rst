New/Mode
==========

`New/Mode <https://www.newmode.net/>`_ is a multi-channel advocacy and civic engagement platform
for organizations and campaigns.

The methods in this class return either individual items as dictionaries or lists of items as
Parsons ``Table`` objects.

The class includes methods for fetching tools, actions, targets, campaigns, organizations, services,
and outreaches. There are also methods for looking up targets and running actions given a ``tool_id``.

.. note::
  Authentication
    To use the class, you need only provide a New/Mode username and password. For more information,
    see `The New/Mode API is Here <https://blog.newmode.net/new-modes-api-is-here-4c4b70c6fce6>`_.

***********
Quick Start
***********

.. code-block:: python

	from parsons import Newmode

	newmode = Newmode(api_user='my_username', api_password='my_password')

	# Get existing tools.
	tools = newmode.get_tools()

	# Get specific tool.
	tool = newmode.get_tool(tool_id)

***
API
***
.. autoclass :: parsons.Newmode
   :inherited-members:
