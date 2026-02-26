Salesforce
==========

`Salesforce <https://www.salesforce.com>`_ is a cloud-based CRM with a huge share of the for-profit
and apolitical non-profit markets.

***********
Quick Start
***********

.. code-block:: python
	
	from parsons import Salesforce, Table

	sf = Salesforce()

	# Get IDs and names for all Contacts
	all_contacts = sf.query("SELECT Id, firstname, lastname FROM Contact")

	# Get IDs, names, and email addresses from Contacts with a specific value for a custom field
	ak_contacts = sf.query("SELECT Id, firstname, lastname, email FROM Contact WHERE digital_source__c == 'AK'")

	# Update existing Contacts and create new records based on data in a Parsons Table
	upsert_results = sf.upsert('Contact', contacts_table, 'id')

***
API
***
.. autoclass :: parsons.Salesforce
   :inherited-members: