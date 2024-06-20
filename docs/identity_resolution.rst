Identity Resolution
===================

********
Overview
********

IDRT (Identity Resolution Transformer) is a library that uses neural networks to identify
duplicate contacts by their contact data, like name and phone.

IDRT contains two main sub-packages: IDRT and IDRT.algorithm. 

* IDRT contains tools that allow you to train your own model based on existing
  duplicate/distinct data.

    * IDRT training produces two models that are used by the algorithm: an *encoder* model
      and a *classifier* model.

* IDRT.algorithm provides functions to run an algorithm that use an IDRT model to 
  perform an efficient duplicate search on a database of contacts. 

This connector does not provide access to the model training portion of the
library. To use it, you must have trained models at hand. It does provide
Parsons integration to the algorithm portion of IDRT, allowing you to easily identify
duplicate contacts in your database.

For more information, see: https://github.com/Jason94/identity-resolution

============
Installation
============

**Step 0: Install PyTorch**

If you're using IDRT for the first time, you can skip to step 1.

IDRT uses the *PyTorch* Python library to build its neural networks.
Neural networks are significantly faster if they're running on graphics cards (GPUs)
as opposed to traditional processors (CPUs). If you have a graphics card in the
computer (or cloud computation platform) where you will be running IDRT, you can 
take advantage of GPU hardware by installing the **CUDA** version of PyTorch.

Visit `the PyTorch installation webpage <https://pytorch.org/get-started/locally/>`_. Select `CUDA 11.8`
and your preferred operating system. It will give you a `pip` command that you can use to install the GPU
version of PyTorch. Run this command.

When you are running the IDRT algorithm, this line will appear in the logs if it is running on CPU hardware:

.. code-block::

    INFO:idrt.algorithm.utils:Found device cpu

and this line will appear if you are running on GPU hardware:

.. code-block::

    INFO:idrt.algorithm.utils:Found device cuda

**Step 1: Install the IDRT Parsons connector**

Because IDRT pulls in several large dependencies, it is not part of the standard Parsons installation.
You can install the IDRT Parsons connector by running this command:

.. code-block::

    pip install parsons[idr]

If you are on newer versions of Pip (>= 20.3) your installation might take an inordinately long time. If
your install is taking a long time and you see log messages like ``INFO: This is taking longer than usual.
You might need to provide the dependency resolver with stricter constraints to reduce runtime. See
https://pip.pypa.io/warnings/backtracking for guidance. If you want to abort this run, press Ctrl + C.``
then you can use this workaround to install Parsons and IDRT separately:

.. code-block::

    pip install parsons
    pip install idrt[algorithm]
    pip install parsons[idr] --no-deps

==========
Quickstart
==========

These scripts will run out-of-the-box, but they assume that you have model files on hand.
The scripts will look for model files named `"encoder.pt"` and `"classifier.pt"` in the directory
where you run the script. If you're running these scripts on some database orchestration platforms,
like Civis Platform, you might need to use URL's instead of file paths to serve the algorithm
files stored in the platform. In that case, you should change the scripts to use the `encoder_url`
parameter for step 1 and the `encoder_url` and `classifier_url` parameters for step 2.

**Example 1**

This script matches all of the contacts stored in a SQL table or view. It will look for an
environmental variable, `SCHEMA`, and a contact data table/view, `DATA_TABLE` in that schema. The
data table must have a `primary_key` column, a `pool` column (it can be set to `NULL`), and a 
column for all of the fields that the model is trained to expect (email, etc). They must also do any
pre-processing that the model has been trained to expect. A common example of pre-processing is
removing any parenthesis, hyphens, and spaces from phone numbers. (See documentation for your
model for more details on individual fields.) Usually we create SQL views to format data from your
sources in a way that can be fed into IDRT, and pass the SQL views into the algorithm as the
`DATA_TABLE`.

The script will run step one, producing an encoding of the first 10,000 rows.
It will then run step two, which will perform a duplicate search among those 10,000 rows.

Finally, it will download all of the contcats that were determined to be duplicates and save them
to a CSV file.

.. code-block:: python

    import os
    import logging

    from parsons.databases.discover_database import discover_database
    from parsons import IDRT

    logging.basicConfig()
    logging.getLogger("idrt.algorithm.prepare_data").setLevel(logging.INFO)
    logging.getLogger("idrt.algorithm.run_search").setLevel(logging.INFO)

    SCHEMA = os.environ["SCHEMA"]
    DATA_TABLE = os.environ["DATA_TABLE"]
    ENCODER_PATH = os.path.join(os.getcwd(), "encoder.pt")
    CLASSIFIER_PATH = os.path.join(os.getcwd(), "classifier.pt")

    full_data_table = SCHEMA + "." + DATA_TABLE

    db = discover_database()
    idrt = IDRT(db, output_schema=SCHEMA)

    idrt.step_1_encode_contacts(full_data_table, limit=10_000, encoder_path=ENCODER_PATH)
    idrt.step_2_run_search(encoder_path=ENCODER_PATH, classifier_path=CLASSIFIER_PATH)

    # For some reason the Parsons Redshift connector uploads boolean datatypes as strings,
    # so we have to compare to the string 'True' if we're running on Redshift.
    duplicates = db.query(
        f""" SELECT d.classification_score, c1.*, c2.*
            FROM {SCHEMA}.idr_dups d
            JOIN {full_data_table} c1
                ON c1.primary_key = d.pkey1
                AND c1.pool = d.pool1
            JOIN {full_data_table} c2
                ON c2.primary_key = d.pkey2
                AND c2.pool = d.pool2
            WHERE d.matches = 'True';
        """
    )
    duplicates.to_csv("duplicates.csv")

**Example 2**

This script extends the previous one to guarantee that it will finish matching all
of the contacts in one run of the script. After we complete step 2, we check to see
if there are any contacts that hadn't been encoded in step 1. *(Encoded contacts are stored
in the `idr_out` table and contacts that the model couldn't read are stored in the
`idr_invalid_contacts` table.)* If we find any, we repeat steps 1 & 2 until all contacts have
been processed and matched.

.. code-block:: python

    import os
    import logging

    from parsons.databases.discover_database import discover_database
    from parsons.databases.database_connector import DatabaseConnector
    from parsons import IDRT

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("idrt.algorithm.prepare_data").setLevel(logging.INFO)
    logging.getLogger("idrt.algorithm.run_search").setLevel(logging.INFO)

    SCHEMA = os.environ["SCHEMA"]
    DATA_TABLE = os.environ["DATA_TABLE"]
    ENCODER_PATH = os.path.join(os.getcwd(), "encoder.pt")
    CLASSIFIER_PATH = os.path.join(os.getcwd(), "classifier.pt")

    full_data_table = SCHEMA + "." + DATA_TABLE

    db = discover_database()
    idrt = IDRT(db, output_schema=SCHEMA)


    def iterate_algorithm(db: DatabaseConnector):
        idrt.step_1_encode_contacts(full_data_table, limit=300, encoder_path=ENCODER_PATH)
        idrt.step_2_run_search(encoder_path=ENCODER_PATH, classifier_path=CLASSIFIER_PATH)

        # If we don't encounter any invalid contacts in the first iteration,
        # the table might not exist yet.
        if db.table_exists(SCHEMA + ".idr_invalid_contacts"):
            remaining_contacts = db.query(
                f"""
                SELECT count(*)
                FROM {full_data_table} c
                LEFT JOIN {SCHEMA}.idr_out out
                    ON out.primary_key = c.primary_key
                    AND out.pool = c.pool
                LEFT JOIN {SCHEMA}.idr_invalid_contacts inv
                    ON inv.primary_key = c.primary_key
                    AND inv.pool = c.pool
                WHERE out.primary_key IS NULL
                    AND inv.primary_key IS NULL;
                """
            ).first
        else:
            remaining_contacts = db.query(
                f"""
                SELECT count(*)
                FROM {full_data_table} c
                LEFT JOIN {SCHEMA}.idr_out out
                    ON out.primary_key = c.primary_key
                    AND out.pool = c.pool
                WHERE out.primary_key IS NULL;
                """
            ).first

        logging.info(f"{remaining_contacts} contacts remaining")
        if remaining_contacts > 0:
            iterate_algorithm(db)


    iterate_algorithm(db)

    # For some reason the Parsons Redshift connector uploads boolean datatypes as strings,
    # so we have to compare to the string 'True' if we're running on Redshift.
    duplicates = db.query(
        f""" SELECT d.classification_score, c1.*, c2.*
            FROM {SCHEMA}.idr_dups d
            JOIN {full_data_table} c1
                ON c1.primary_key = d.pkey1
                AND c1.pool = d.pool1
            JOIN {full_data_table} c2
                ON c2.primary_key = d.pkey2
                AND c2.pool = d.pool2
            WHERE d.matches = 'True';
        """
    )
    duplicates.to_csv("duplicates.csv")

**Example 3**

This script brings in the notion of *pools*. The simpler scripts above can identify
duplicates within one set of contacts. They cannot identify, for example, the contact
in your ActionKit data that best matches a given contact in your EveryAction data. 
This kind of cross-matching can be accomplished using the source and search pools
arguments to step 2.

The code below will run step 1 against two source tables, one containing the contact data
for EveryAction and one containing the contact data for ActionKit. These tables must
be formatted the same way as the previous ones. The EveryAction table must contain
`everyaction` in the `pool` column for all rows, and the ActionKit table must contain
`actionkit` in the `pool` column for all rows.

.. code-block:: python

    import os
    import logging

    from parsons.databases.discover_database import discover_database
    from parsons import IDRT

    logging.basicConfig()
    logging.getLogger("idrt.algorithm.prepare_data").setLevel(logging.INFO)
    logging.getLogger("idrt.algorithm.run_search").setLevel(logging.INFO)

    SCHEMA = os.environ["SCHEMA"]
    EA_DATA_TABLE = os.environ["EA_DATA_TABLE"]
    AK_DATA_TABLE = os.environ["AK_DATA_TABLE"]
    ENCODER_PATH = os.path.join(os.getcwd(), "encoder.pt")
    CLASSIFIER_PATH = os.path.join(os.getcwd(), "classifier.pt")

    full_ea_table = SCHEMA + "." + EA_DATA_TABLE
    full_ak_table = SCHEMA + "." + AK_DATA_TABLE

    db = discover_database()
    idrt = IDRT(db, output_schema=SCHEMA)

    idrt.step_1_encode_contacts(full_ea_table, limit=10_000, encoder_path=ENCODER_PATH)
    idrt.step_1_encode_contacts(full_ak_table, limit=10_000, encoder_path=ENCODER_PATH)
    idrt.step_2_run_search(
        encoder_path=ENCODER_PATH,
        classifier_path=CLASSIFIER_PATH,
        source_pool="everyaction",
        search_pool="actionkit",
    )

    # For some reason the Parsons Redshift connector uploads boolean datatypes as strings,
    # so we have to compare to the string 'True' if we're running on Redshift.
    duplicates = db.query(
        f""" SELECT d.classification_score, c1.*, c2.*
            FROM {SCHEMA}.idr_dups d
            JOIN {full_ea_table} c1
                ON c1.primary_key = d.pkey1
                AND c1.pool = d.pool1
            JOIN {full_ak_table} c2
                ON c2.primary_key = d.pkey2
                AND c2.pool = d.pool2
            WHERE d.matches = 'True';
        """
    )
    duplicates.to_csv("duplicates.csv")

***
API
***

.. autoclass :: parsons.IDRT
   :inherited-members:
