Bill.com
==========

********
Overview
********

`Bill.com <https://www.bill.com>`_ is an online billing and invoicing tool. This class contains methods to:

- Get lists of customers, users, and invoices
- Read, create, and send invoices
- Read, create, and get customers
- Check whether two customers are the same

For more information, see `Bill.com developer docs <https://developer.bill.com/hc/en-us/categories/360002253732>`_

.. note::

  Authentication
    To instantiate the ``BillCom`` class, you must provide the username and password you used to sign
    up for Bill.com, and the Organization ID and Dev Key you received when API access was granted.

***********
Quick Start
***********

Your Username, Password, Organization ID, and Dev Key must be provided as arguments.

.. code-block:: python

    from parsons import BillCom

    bc = BillCom(username='my_username',
                 password='my_password',
                 org_id='my_org_id',
                 dev_key='my_dev_key',
                 api_url='https://api-sandbox.bill.com/api/v2/')

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

.. autoclass:: parsons.bill_com.bill_com.BillCom
   :inherited-members:
   :members:
   