Action Network
==========

`Action Network <https://actionnetwork.org/>`_ is an online tool for storing information
about and organizing volunteers and donors. For more information, see `Action Network developer docs <https://actionnetwork.org/docs>`_

***********
Quick Start
***********

.. code-block:: python
	
	from parsons import ActionNetwork, Table

	an = ActionNetwork(API_TOKEN)

	# List all people stored in Action Network
	all_contacts = an.get_people_list()

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
