############
Google Admin
############

Overview
========

The GoogleAdmin class allows you to get information about groups and members in Google Admin.

In order to instantiate the class, you must pass Google service account credentials as a dictionary,
or store the credentials as a JSON string in the ``GOOGLE_APPLICATION_CREDENTIALS`` environment variable.
You must also provide an email address for `domain-wide delegation <https://developers.google.com/admin-sdk/directory/v1/guides/delegation>`_.

Quickstart
==========

To instantiate the GoogleAdmin class, you can either pass the constructor a dict containing your Google service account credentials or define the environment variable ``GOOGLE_APPLICATION_CREDENTIALS`` to contain a JSON encoding of the dict.

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import GoogleAdmin
   admin = GoogleAdmin(None, 'fakeemail@fakedomain.com')

.. code-block:: python
   :caption: Pass API credentials as argument

   from parsons import GoogleAdmin
   credential_filename = 'google_application_credentials.json'
   credentials = json.load(open(credential_filename))
   sheets = GoogleAdmin(credentials, 'fakeemail@fakedomain.com')

.. code-block:: python
   :caption: Get information about groups and members using instance methods

   members = admin.get_all_group_members('group_key')
   groups = admin.get_all_groups(domain='fakedomain.com')

API
====

.. autoclass:: parsons.google.google_admin.GoogleAdmin
   :inherited-members:
   :members:
