import pytest
from parsons.etl import Table


"""
Simple Table

The bare minimum Parsons table, and matching files representing that table.
"""


@pytest.fixture
def simple_table():
    # Note - If you modify this table, you must also update the related "simple" files.
    # Fortunately Parsons should make that easy to do :)
    return Table([{"first": "Bob", "last": "Smith"}])


@pytest.fixture
def simple_csv_path(shared_datadir):
    return str(shared_datadir / "test-simple-table.csv")


@pytest.fixture
def simple_compressed_csv_path(shared_datadir):
    return str(shared_datadir / "test-simple-table.csv.gz")
