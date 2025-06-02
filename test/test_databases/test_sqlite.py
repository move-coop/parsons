import tempfile
import unittest

from parsons import Table
from parsons.databases.sqlite import Sqlite
from test.utils import assert_matching_tables


class TestSqlite(unittest.TestCase):
    def setUp(self):
        temp_db = tempfile.mkstemp(suffix=".db")[1]
        self.sqlite = Sqlite(temp_db)

        self.tbl = Table([["ID", "Name"], [1, "Jim"], [2, "John"], [3, "Sarah"]])

    def test_copy(self) -> None:
        self.sqlite.copy(self.tbl, "tbl1", if_exists="drop")
        tbl1_read = self.sqlite.query("select * from tbl1")
        assert_matching_tables(self.tbl, tbl1_read)

    def test_copy_no_cli(self) -> None:
        self.sqlite.copy(self.tbl, "tbl1", if_exists="drop", force_python_sdk=True)
        tbl1_read = self.sqlite.query("select * from tbl1")
        assert_matching_tables(self.tbl, tbl1_read)

    def test_copy_append(self) -> None:
        self.sqlite.copy(self.tbl, "tbl1", if_exists="drop")
        self.sqlite.copy(self.tbl, "tbl1", if_exists="append")
        row_count = self.sqlite.query("select count(*) as count from tbl1")
        assert row_count[0]["count"] == 6

    def test_copy_fail(self) -> None:
        self.sqlite.copy(self.tbl, "tbl1", if_exists="drop")
        try:
            # This line should raise a ValueError
            self.sqlite.copy(self.tbl, "tbl1", if_exists="fail")
            # so this line should not be executed
            raise AssertionError("should have failed")
        except ValueError:
            pass

    def test_copy_truncate(self) -> None:
        self.sqlite.copy(self.tbl, "tbl1", if_exists="drop")
        self.sqlite.copy(self.tbl, "tbl1", if_exists="truncate")
        row_count = self.sqlite.query("select count(*) as count from tbl1")
        assert row_count[0]["count"] == 3


if __name__ == "__main__":
    unittest.main()
