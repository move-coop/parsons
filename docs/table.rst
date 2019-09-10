.. _parsons-table:

Parsons Table
=============


********
Overview
********

Most methods and functions in Parsons return a ``Table``, which is a 2D list-like object. (It's similar to a pandas DataFrame, if you are familiar with that). You can call the following methods on the returned object to output it into a variety of formats or storage types. (For a full list of ``Table`` methods, scroll down to the class documentation.)

===================
From Parsons Table
===================

.. list-table::
    :widths: 25 25 50
    :header-rows: 1

    * - Method
      - Destination Type
      - Description
    * - ``.to_dataframe()``
      - Dataframe
      - Return a Pandas dataframe
    * - ``.to_csv()``
      - CSV File
      - Write a table to a local csv file
    * - ``.to_s3_csv()``
      - AWS s3 Bucket
      - Write a table to a csv stored in S3
    * - ``.to_redshift()``
      - A Redshift Database
      - Write a table to a Redshift database
    * - ``.to_civis()``
      - Civis Redshift Database
      - Write table to a Civis Redshift Database using Civis Client
    * - ``.to_petl()``
      - Petl table object
      - Convert a table a Petl table object
    * - ``.to_json()``
      - JSON file
      - Write a table to a local JSON file
    * - ``.to_html()``
      - HTML formatted table
      - Write a table to a local html file

================
To Parsons Table
================

Create Parsons Table object using the following methods.

.. list-table::
    :widths: 25 25 50
    :header-rows: 1

    * - Method
      - Source Type
      - Description
    * - ``.from_csv()``
      - File like object, local path, url, ftp.
      - Loads a csv object into a Table
    * - ``.from_json()``
      - File like object, local path, url, ftp.
      - Loads a json object into a Table
    * - ``.from_columns()``
      - List object
      - Loads lists organized as columns in Table
    * - ``.from_redshift()``
      - Redshift table
      - Loads a Redshift table into a Table
    * - ``.from_dataframe()``
      - Pandas Dataframe
      - Load a Parsons table from a Pandas Dataframe

You can also use the Table constructor to create a Table from a python list or petl table:

.. code-block:: python

    # From a list of dicts
    tbl = Table([{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])

    # From a list of lists, the first list holding the field names
    tbl = Table([['a', 'b'], [1, 2], [3, 4]])

    # From a petl table
    tbl = Table(petl_tbl)

========================
Parsons Table Attributes
========================

.. list-table::
    :widths: 25 50
    :header-rows: 1

    * - Attribute
      - Description
    * - ``.num_rows``
      - The number of rows in the table
    * - ``.columns``
      - A list of column names in the table
    * - ``.data``
      - The actual data (rows) of the table, as a list of tuples (without field names)


A note on indexing and iterating over a table's data:
If you need to iterate over the data, make sure to use the python iterator syntax, so any data transformations can be applied efficiently. An example:

.. code-block:: python

    # Some data transformations
    table.add_column('newcol', 'some value')

    # Efficient way to grab all the data (applying the data transformations only once)
    rows_list = [row for row in table]

.. warning::
   If you must index directly into a table's data, you can do so, but note that data transformations will be applied **each time** you do so. So this code will be very inefficient on a large table...

.. code-block:: python

    # Inefficient way to grab all the data
    rows_list = []
    for i in range(0, table.num_rows):
      # Data transformations will be applied each time through this loop!
      rows_list.append(table[i])

====
PETL
====

The Parsons ``Table`` relies heavily on the `petl <https://petl.readthedocs.io/en/stable/index.html>`_ Python package. You can always access the underlying petl table with ``my_parsons_table.table``, which will allow you to perform any petl-supported ETL operations.

============
Lazy Loading
============

The Parsons ``Table`` makes use of "lazy" loading and "lazy" transformations. What this means is that it tries not to load and process your data until absolutely necessary.

An example:

.. code-block:: python

  # Specify where to load the data
  tbl = Table.from_csv('name_data.csv')

  # Specify data transformations
  tbl.add_column('full_name', lambda row: row['first_name'] + ' ' + row['last_name'])
  tbl.remove_column(['first_name', 'last_name'])

  # Save the table elsewhere
  # IMPORTANT - The CSV won't actually be loaded and transformed until this step,
  # since this is the first time it's actually needed.
  tbl.to_redshift('main.name_table')

This "lazy" loading can be very convenient and performant. However, it can make issues hard to debug. Eg. if your data transformations are time-consuming, you won't actually notice that performance hit until you try to use the data, potentially much later in your code.

So just be aware of this behavior.

********
Examples
********

===============
Basic Pipelines
===============

.. code-block:: python

    # S3 to Civis
    s3 = S3()
    csv = s3.get_file('tmc-bucket', 'my_ids.csv')
    Table.from_csv(csv).to_civis('TMC','ids.my_ids')

    #VAN Activist Codes to a Dataframe
    van = VAN(db='MyVoters')
    van.activist_codes().to_dataframe()

    #VAN Events to an s3 bucket
    van = VAN(db='MyVoters')
    van.events().to_s3_csv('my-van-bucket','myevents.csv')


*****************
To & From Methods
*****************
.. autoclass:: parsons.etl.tofrom.ToFrom
   :inherited-members:

***
ETL
***
The following methods allow you to manipulate the Parsons table data.

.. autoclass:: parsons.etl.etl.ETL
   :inherited-members: