Bill.com
==========

`Bill.com <https://www.bill.com>`_ is an online billing and invoicing tool. For more information,
see `Bill.com developer docs <https://developer.bill.com/hc/en-us/categories/360002253732>`_

***********
Quick Start
***********

.. code-block:: python
	
	from parsons import BillCom

	bc = BillCom(USERNAME, PASSWORD, ORG_ID, DEV_KEY, ENDPOINT_URL)

	# List all Customers currently in the system
	all_contacts = bc.get_customer_list()

	# Create a new customer
	customer_data = {
	    "contactFirstName": "Contact First Name",
	}
	bc.create_customer('Customer Name', 'customer.email@fakeemail.com', customer_data)

***
API
***
.. autoclass :: parsons.BillCom
   :inherited-members: