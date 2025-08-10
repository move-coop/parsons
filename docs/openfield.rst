OpenField
=========

********
Overview
********

`OpenField <https://openfield.ai/>`_ is a canvassing and VPB tool for organizing and election campaigns.
`OpenField REST API <https://openfield.ai/wp-content/uploads/2024/02/redoc-static.html>`_

.. note::
  Authentication
    OpenField requires `HTTP Basic Auth <https://en.wikipedia.org/wiki/Basic_access_authentication>`_.
    Clients with an OpenField account can obtain the domain, username, and password needed
    to access the OpenField API.

**********
Quickstart
**********

To instantiate the OpenField class, you can either store your OpenField API
domain, username, and password as environmental variables (``OPENFIELD_DOMAIN``,
``OPENFIELD_USERNAME``, and ``OPENFIELD_PASSWORD``, respectively) or pass in your
domain, username, and password as arguments:

.. code-block:: python

   from parsons import OpenField

   # First approach: Use API credentials via environmental variables
   openfield = OpenField()

   # Second approach: Pass API credentials as arguments
   openfield = OpenField(domain='myorg.openfield.ai', username='my_name', password='1234')

You can then call various endpoints:

.. code-block:: python

    # Create a new person
    person = {
      "first_name": 'John', 
      "last_name": 'Smith', 
      "prov_city": 'Boston', 
      "prov_state": 'MA', 
      "prov_zip_5": '02108'  
      "email1": 'john@email.com', 
      "phone1": '2345678901',
    }
    openfield.create_person(person=person)

    # Fetch person
    person = openfield.retrieve_person(person_id=123)

    # Update person fields
    data= {
      "phone1": '5558765432',
    }
    updated_person = openfield.update_person(person_id=123, data=data)

    # Delete person
    openfield.destroy_person(person_id=123)

***
API
***

.. autoclass :: parsons.OpenField
   :inherited-members:
