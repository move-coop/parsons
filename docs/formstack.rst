Formstack
===================

********
Overview
********

`Formstack <https://www.formstack.com/>`_ is a service that provides an advanced online form builder.
This connector allows you to load data from the Formstack API.

.. note::

  Authentication
    Formstack uses OAuth2 user access tokens to handle authentication. *"Access tokens are tied to a
    Formstack user and follow Formstack (in-app) user permissions."* You can acquire an OAuth2 token
    in the `Formstack API overview <https://developers.formstack.com/reference/api-overview>`_.

    You can pass the token to the ``Formstack`` object as the `api_token` keyword argument, or you
    can set the environment variable ``FORMSTACK_API_TOKEN``.

***********
Quick Start
***********

To instantiate the ``Formstack`` class, you can either store your access token in the ``FORMSTACK_API_TOKEN``
environment variable or pass it in as an argument.

.. code-block:: python

    from parsons.formstack import Formstack

    # Instantiate the Formstack class using the FORMSTACK_API_TOKEN env variable
    fs = Formstack()

    # Instantiate the Formstack class using the api token directly
    fs = Formstack(api_token="<your api token>")

    # Get all of the folders in our account
    folders = fs.get_folders()

    # Find the ID of the "Data" folder
    data_folder_id = None
    for folder in folders:
        if folder["name"] == "Data":
            data_folder_id = folder["id"]
            break

    # If we found the "Data" folder, get all of the forms in it
    if data_folder_id is not None:
        forms = fs.get_forms(folder_id=data_folder_id)

        print(forms)

***
API
***

.. autoclass:: parsons.formstack.formstack.Formstack
   :inherited-members:
   :members:
   