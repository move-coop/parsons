Hustle
======

Hustle is a peer to peer texting communication platform. The methods are built against the `Hustle v1 API <https://api.hustle.com/docs/>`_.

* Access to the API is limited to 100 requests per second for endpoints returning resources. When this limit is reached the API will return an error and the request will need to be retried.

* Creating an access token is an exception in that it only limits the number of failed attempts to create an access token. After 10 failed attempts to create an access token the ip of the request will be blocked for some period of time, but only for the account in question. Additionally 100 failed attempts in a 24-hour period will result in the requester's ip being blocked.

***********
Quick Start
***********

.. code-block:: python

	hustle = Hustle(client_secret='MYID', client_secret='MYSECRET')

	# Export your groups to a csv
	tbl = hustle.get_groups(organization_id='ORGID')
	tbl.to_csv('my_hustle_groups.csv')

	# Export organizations to Redshift
	tbl.get_organizations().to_redshift('hustleschema.hustle_organizations')

	# Import leads from a csv
	leads = Table.from_csv('my_leads.csv')
	group_id = 'MYGROUP'
	hustle.create_leads(leads, group_id)

*******
Methods
*******

.. autoclass :: parsons.Hustle
   :inherited-members:
   :members: