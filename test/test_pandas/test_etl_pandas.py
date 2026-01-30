"""Tests for pandas DataFrame conversion methods"""

import pytest

from parsons import Table
from test.conftest import assert_matching_tables

pd = pytest.importorskip("pandas")


def test_from_dataframe(sample_data):
    # Assert creates table without index
    tbl = Table(sample_data["lst"])
    tbl_from_df = Table.from_dataframe(tbl.to_dataframe())
    assert_matching_tables(tbl, tbl_from_df)


def test_to_dataframe(tbl):
    # Is a dataframe
    assert isinstance(tbl.to_dataframe(), pd.core.frame.DataFrame)
