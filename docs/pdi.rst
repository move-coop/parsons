PDI
===

********
Overview
********

The PDI class allows you to interact with an `PDI's API <https://api.bluevote.com/docs/index#>`_ .

In order to instantiate the class you must pass valid kwargs or store the following
environmental variables:

* ``'PDI_USERNAME'``
* ``'PDI_PASSWORD'``
* ``'PDI_API_TOKEN'``


**********
Quickstart
**********

**Get Contacts**

.. code-block:: python

  pdi = PDI()

  pdi.get_flag_ids()

**************
PDI Class
**************

.. autoclass :: parsons.PDI
    :inherited-members:
