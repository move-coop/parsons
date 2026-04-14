########
Postgres
########

Postgres is popular open source SQL database dialect. The Parsons class leverages the `psycopg2 <https://www.psycopg.org/>`_ python package.

Quickstart
==========

.. code-block:: python
   :caption: Instantiate Postgres from environmental variables
   :emphasize-lines: 2

   from parsons import Postgres
   pg = Postgres()

.. code-block:: python
   :caption: Instantiate Postgres from passed variables
   :emphasize-lines: 2

   from parsons import Postgres
   pg = Postgres(username='me', password='secret', host='mydb.com', db='dev', port=3306)

.. code-block:: python
   :caption: Instantiate Postgres from a ~/.pgpass file
   :emphasize-lines: 2

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
