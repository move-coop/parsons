YourConnector
=============

********
Overview
********

Provide a brief description of the tool your connector integrates with.

Describe which features your connector implements and which features it doesn't. For example,
you could specify that `YourConnector` implements the `thing` and `place` endpoints of the API, but
does not implement the `person` endpoints.

==========
Quickstart
==========

Provide a few examples of how to use `YourConnector`. Each example should be limited to a
few lines of code. Use the [Sphinx Markup syntax](https://www.sphinx-doc.org/en/1.5/markup/code.html)
to embed your examples. Be sure to provide an explanation of exactly what the code is doing.

**Example 1**

.. code-block:: python

  from parsons import YourConnector
  yc = YourConnector()
  table = yc.get_things(updated_since='2020-01-01')

This example shows how to get all of the things updated since the first day of the year 2020.

***
API
***

.. autoclass:: parsons.yourconnector.yourconnector.YourConnector
   :inherited-members:
   :members:
   