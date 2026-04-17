#####
MySQL
#####

MySQL is the world's most popular open source database. The Parsons class leverages on the `MySQLdb1 <https://github.com/farcepest/MySQLdb1>`__ python package.

Quickstart
==========

.. code-block:: python
   :caption: Instantiate MySQL from environmental variables

   from parsons import MySQL
   mysql = MySQL()

.. code-block:: python
   :caption: Instantiate MySQL from passed variables

   from parsons import MySQL
   mysql = MySQL(username='me', password='secret', host='mydb.com', db='dev', port=3306)

.. code-block:: python
   :caption: Query database

   tbl = mysql.query('select * from my_schema.secret_sauce')

.. code-block:: python
   :caption: Copy data to database

   tbl = Table.from_csv('my_file.csv') # Load from a CSV or other source.
   mysql.copy(tbl, 'my_schema.winning_formula')

API
====

.. autoclass:: parsons.databases.mysql.mysql.MySQL
   :inherited-members:
   :members:
