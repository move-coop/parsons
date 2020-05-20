PDI
===

********
Overview
********

`PDI is a political data provider that is primarily active in California.
`The PDI class allows you to interact with an `PDI's API <https://api.bluevote.com/docs/index#>`_ .

In order to instantiate the class you must pass valid kwargs or store the following
environmental variables:

* ``'PDI_USERNAME'``
* ``'PDI_PASSWORD'``
* ``'PDI_API_TOKEN'``


**********
Quickstart
**********

.. code-block:: python

  from parsons import PDI

  pdi = PDI()

  #Get all contacts (flag IDs) available from PDI
  pdi.get_flag_ids()

  #Get all flags since the beginning of 2020
  pdi.get_flags(start_date='2020-01-01')

**************
PDI Class
**************

.. autoclass :: parsons.PDI
    :inherited-members:
