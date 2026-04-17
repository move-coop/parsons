#############
YourConnector
#############

Overview
========

Provide a brief description of the tool your connector integrates with.

Describe which features your connector implements and which features it doesn't.
For example, you could specify that ``YourConnector`` implements the ``thing`` and ``place`` endpoints of the API,
but does not implement the ``person`` endpoints.

Quickstart
==========

Provide a few examples of how to use ``YourConnector``. Each example should be limited to a few lines of code.
Use the `Sphinx Markup syntax <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code>`__
to embed your examples. Be sure to provide an explanation of exactly what the code is doing.

.. code-block:: python
   :caption: Get all things updated since Jan 01 2020

   from parsons import YourConnector
   yc = YourConnector()
   table = yc.get_things(updated_since='2020-01-01')

API
====

.. autoclass:: parsons.yourconnector.yourconnector.YourConnector
   :inherited-members:
   :members:
