.. _parsons-table:

Parsons Table
=============


********
Overview
********

Most methods and functions in Parsons return a ``Table``, which is a 2D list-like object similar to a Pandas Dataframe. You can call the following methods on the Table object to output it into a variety of formats or storage types. A full list of ``Table`` methods can be found in the API section.

===================
From Parsons Table
===================

.. list-table::
    :widths: 25 25 50
    :header-rows: 1

    * - Method
      - Destination Type
      - Description
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_csv`
      - CSV File
      - Write a table to a local csv file
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_s3_csv`
      - AWS s3 Bucket
      - Write a table to a csv stored in S3
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_gcs_csv`
      - Google Cloud Storage Bucket
      - Write a table to a csv stored in Google Cloud Storage
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_sftp_csv`
      - SFTP Server
      - Write a table to a csv stored on an SFTP server
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_redshift`
      - A Redshift Database
      - Write a table to a Redshift database
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_postgres`
      - A Postgres Database
      - Write a table to a Postgres database
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_civis`
      - Civis Redshift Database
      - Write a table to Civis platform database
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_petl`
      - Petl table object
      - Convert a table a Petl table object
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_json`
      - JSON file
      - Write a table to a local JSON file
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_html`
      - HTML formatted table
      - Write a table to a local html file
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_dataframe`
      - Pandas Dataframe [1]_
      - Return a Pandas dataframe
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.append_csv`
      - CSV file
      - Appends table to an existing CSV
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_zip_csv`
      - ZIP file
      - Writes a table to a CSV in a zip archive
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.to_dicts`
      - Dicts
      - Write a table as a list of dicts


.. [1] Requires optional installation of Pandas package by running ``pip install pandas``.

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
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.from_csv`
      - File like object, local path, url, ftp.
      - Loads a csv object into a Table
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.from_json`
      - File like object, local path, url, ftp.
      - Loads a json object into a Table
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.from_columns`
      - List object
      - Loads lists organized as columns in Table
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.from_redshift`
      - Redshift table
      - Loads a Redshift query into a Table
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.from_postgres`
      - Postgres table
      - Loads a Postgres query into a Table
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.from_dataframe`
      - Pandas Dataframe [2]_
      - Load a Parsons table from a Pandas Dataframe
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.from_s3_csv`
      - S3 CSV
      - Load a Parsons table from a csv file on S3
    * - :py:meth:`~parsons.etl.tofrom.ToFrom.from_csv_string`
      - File like object, local path, url, ftp.
      - Load a CSV string into a Table

.. [2] Requires optional installation of Pandas package by running ``pip install pandas``.

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

Tables have a number of convenience attributes.

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
    * - ``.first``
      - The first value in the table. Use for database queries where a single value is returned.

=============================
Parsons Table Transformations
=============================

Parsons tables have many methods that allow you to easily transform tables. Below is a selection
of commonly used methods. The full list can be found in the API section.

**Column Transformations**

.. list-table::
    :widths: 40 200
    :header-rows: 1

    * - Method
      - Description
    * - :py:meth:`~parsons.etl.etl.ETL.add_column`
      - Add a column
    * - :py:meth:`~parsons.etl.etl.ETL.remove_column`
      - Remove a column
    * - :py:meth:`~parsons.etl.etl.ETL.rename_column`
      - Rename a column
    * - :py:meth:`~parsons.etl.etl.ETL.move_column`
      - Move a column within a table
    * - :py:meth:`~parsons.etl.etl.ETL.cut`
      - Return a table with a subset of columns
    * - :py:meth:`~parsons.etl.etl.ETL.fill_column`
      - Provide a fixed value to fill a column
    * - :py:meth:`~parsons.etl.etl.ETL.fillna_column`
      - Provide a fixed value to fill all null values in a column
    * - :py:meth:`~parsons.etl.etl.ETL.get_column_types`
      - Get the python type of values for a given column
    * - :py:meth:`~parsons.etl.etl.ETL.convert_column`
      - Transform the values of a column via arbitrary functions
    * - :py:meth:`~parsons.etl.etl.ETL.coalesce_columns`
      - Coalesce values from one or more source columns
    * - :py:meth:`~parsons.etl.etl.ETL.map_columns`
      - Standardizes column names based on multiple possible values


**Row Transformations**

.. list-table::
    :widths: 25 50
    :header-rows: 1

    * - Method
      - Description
    * - :py:meth:`~parsons.etl.etl.ETL.select_rows`
      - Return a table of a subset of rows based on filters
    * - :py:meth:`~parsons.etl.etl.ETL.stack`
      - Stack a number of tables on top of one another
    * - :py:meth:`~parsons.etl.etl.ETL.chunk`
      - Divide tables into smaller tables based on row count
    * - :py:meth:`~parsons.etl.etl.ETL.remove_null_rows`
      - Removes rows with null values in specified columns


**Extraction and Reshaping**

.. list-table::
    :widths: 25 50
    :header-rows: 1

    * - Method
      - Description
    * - :py:meth:`~parsons.etl.etl.ETL.unpack_dict`
      - Unpack dictionary values from one column to top level columns
    * - :py:meth:`~parsons.etl.etl.ETL.unpack_list`
      - Unpack list values from one column and add to top level columns
    * - :py:meth:`~parsons.etl.etl.ETL.long_table`
      - Take a column with nested data and create a new long table
    * - :py:meth:`~parsons.etl.etl.ETL.unpack_nested_columns_as_rows`
      - Unpack list or dict values from one column into separate rows


======================
Parsons Table Indexing
======================

To access rows and columns of data within a Parsons table, you can index on them. To access a column
pass in the column name as a string (e.g. ``tbl['a']``) and to access a row, pass in the row index as
an integer (e.g. ``tbl[1]``).

.. code-block:: python

    tbl = Table([{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])

    # Return a column as a list
    tbl['a']
    >> [1, 3]

    # Return a row as a dict
    tbl[1]
    >> {'a': 3, 'b': 4}

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

The Parsons ``Table`` relies heavily on the `petl <https://petl.readthedocs.io/en/stable/index.html>`_
Python package. You can always access the underlying petl table, ``parsons.Table.table``, which will
allow you to perform any petl-supported ETL operations. Additionally, you can use the helper method,
:py:meth:`~parsons.etl.etl.ETL.use_petl`, to conveniently perform the same operations on a parsons
``Table``. For example:

.. code-block:: python

  import petl
  ...

  tbl = Table()
  tbl.table = petl.skipcomments(tbl.table, '#')

or

.. code-block:: python

  tbl = Table()
  tbl.use_petl('skipcomments', '#', update_table=True)

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


*************
To & From API
*************
.. autoclass:: parsons.etl.tofrom.ToFrom
   :inherited-members:

******************
Transformation API
******************
The following methods allow you to manipulate the Parsons table data.

.. autoclass:: parsons.etl.etl.ETL
   :inherited-members:
