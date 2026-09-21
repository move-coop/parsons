########
Postgres
########

.. admonition:: Required Extra

   To use the Postgres connector, you will need to install parsons with the postgres extra.
   To do this, you will need to install it with ``pip install parsons[postgres]`` or ``pip install parsons[all]``.

Overview
========

Postgres is popular open source SQL database dialect.
The Parsons class leverages the `psycopg2 <https://www.psycopg.org/>`__ python package.

Quickstart
==========

.. code-block:: python
   :caption: Instantiate Postgres from environmental variables

   from parsons import Postgres
   pg = Postgres()

.. code-block:: python
   :caption: Instantiate Postgres from passed variables

   from parsons import Postgres
   pg = Postgres(username='me', password='secret', host='mydb.com', db='dev', port=3306)

.. code-block:: python
   :caption: Instantiate Postgres from a ~/.pgpass file

   from parsons import Postgres
   pg = Postgres()

.. code-block:: python
   :caption: Query database

   tbl = pg.query('select * from my_schema.secret_sauce')

.. code-block:: python
   :caption: Copy data to database

   tbl = Table.from_csv('my_file.csv') # Load from a CSV or other source.
   pg.copy(tbl, 'my_schema.winning_formula')

API
====

.. autoclass:: parsons.databases.postgres.postgres.Postgres
   :inherited-members:
   :members:
