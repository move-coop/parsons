Action Network
==========

********
Overview
********

`Action Network <https://actionnetwork.org/>`_ is an online tool for storing information
and organizing volunteers and donors. It is used primarily for digital organizing and event mangement. For more information, see `Action Network developer docs <https://actionnetwork.org/docs>`_

.. note::
  Authentication
  	Only ActionNetwork accounts of the partner tier are able to access their API. You can generate your key from the API & Sync page, located in the *Start Organizing* menu, under *Details*.

***********
Quick Start
***********

To instantiate a class, you can either pass in the API token as an argument or set the ``AN_API_TOKEN`` environmental variable.

.. code-block:: python

   from parsons import ActionNetwork

   # First approach: Use API credentials via environmental variables
   an = ActionNetwork()

   # Second approach: Pass API credentials as arguments
   an = ActionNetwork(api_token='MY_API_TOKEN')

You can then call various endpoints:

.. code-block:: python

	# List all people stored in Action Network
	all_contacts = an.get_people()

	# Add a person
	an.add_person('person.email@fakeemail.com')

	# Add a tag
	an.add_tag('fake_tag')

	# Update a person
	an.update_person('fake_id', given_name='new_given_name', tags=['tag_1', 'tag_2'])

***
API
***
.. autoclass :: parsons.ActionNetwork
   :inherited-members:
