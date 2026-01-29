import pytest

from parsons import Table
from test.conftest import assert_matching_tables
from test.test_etl import BaseTableTest

pd = pytest.importorskip("pandas")


class TestPandasMethods(BaseTableTest):
    def test_from_datafame(self):
        # Assert creates table without index
        tbl = Table(self.lst)
        tbl_from_df = Table.from_dataframe(tbl.to_dataframe())
        assert_matching_tables(tbl, tbl_from_df)

    def test_to_dataframe(self):
        # Is a dataframe
        assert isinstance(self.tbl.to_dataframe(), pd.core.frame.DataFrame)
