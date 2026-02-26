New/Mode
==========

`New/Mode <https://www.newmode.net/>`_ is the multi-channel advocacy & civic engagement platform
for organizations and campaigns.

Most methods and functions in Parsons return a ``Table``, which is a 2D list-like object. Read
more in Table documentation.

***********
Quick Start
***********

.. code-block:: python

	from parsons import Newmode

	newmode = Newmode(api_user='XXXX', api_password='XXXX')

	# Get existing tools.
	tools = newmode.get_tools()

	# Get specific tool.
	tool = newmode.get_tool(tool_id)

***
API
***
.. autoclass :: parsons.Newmode
   :inherited-members:
