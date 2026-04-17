#########
Formstack
#########

Overview
========

`Formstack <https://www.formstack.com/>`_ is a service that provides an advanced online form builder.
This connector allows you to load data from the Formstack API.

.. admonition:: Authentication

   Formstack uses OAuth2 user access tokens to handle authentication. *"Access tokens are tied to a
   Formstack user and follow Formstack (in-app) user permissions."* You can acquire an OAuth2 token
   in the `Formstack API overview <https://developers.formstack.com/reference/api-overview>`_.

   You can pass the token to the :class:`~parsons.formstack.formstack.Formstack` object as the `api_token` keyword argument, or you
   can set the environment variable ``FORMSTACK_API_TOKEN``.

Quickstart
==========

To instantiate the :class:`~parsons.formstack.formstack.Formstack` class, you can either store your access token in the ``FORMSTACK_API_TOKEN``
environment variable or pass it in as an argument.

.. code-block:: python
   :caption: Instantiate the Formstack class using the ``FORMSTACK_API_TOKEN`` environment variable

   from parsons.formstack import Formstack
   fs = Formstack()

.. code-block:: python
   :caption: Instantiate the Formstack class using the api token directly

   from parsons.formstack import Formstack
   fs = Formstack(api_token="<your api token>")

.. code-block:: python
   :caption: Find the ID of folder "Data" and get all the forms in it

   folders = fs.get_folders()
   data_folder_id = None
   for folder in folders:
      if folder["name"] == "Data":
         data_folder_id = folder["id"]
         break

   if data_folder_id is not None:
      forms = fs.get_forms(folder_id=data_folder_id)
      print(forms)

API
====

.. autoclass:: parsons.formstack.formstack.Formstack
   :inherited-members:
   :members:
