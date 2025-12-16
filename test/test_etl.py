import shutil
import tempfile
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import petl
import pytest

from parsons import Table
from parsons.utilities import zip_archive
from test.utils import assert_matching_tables

# Notes :
# - The `Table.to_postgres()` test is housed in the Postgres tests
# - The `Table.from_postgres()` test is housed in the Postgres test


class TestParsonsTable(unittest.TestCase):
    def setUp(self):
        # Create Table object
        self.lst = [
            {"a": 1, "b": 2, "c": 3},
            {"a": 4, "b": 5, "c": 6},
            {"a": 7, "b": 8, "c": 9},
            {"a": 10, "b": 11, "c": 12},
            {"a": 13, "b": 14, "c": 15},
        ]
        self.lst_dicts = [{"first": "Bob", "last": "Smith"}]
        self.tbl = Table(self.lst_dicts)

        # Create a tmp dir
        self.tmp_folder = tempfile.mkdtemp()

    def tearDown(self):
        # Delete tmp folder and files
        shutil.rmtree(self.tmp_folder)

    def test_from_list_of_dicts(self):
        tbl = Table(self.lst)

        # Test Iterate and is list like
        assert tbl[0] == {"a": 1, "b": 2, "c": 3}

    def test_from_list_of_lists(self):
        list_of_lists = [
            ["a", "b", "c"],
            [1, 2, 3],
            [4, 5, 6],
        ]
        tbl = Table(list_of_lists)

        assert tbl[0] == {"a": 1, "b": 2, "c": 3}

    def test_from_petl(self):
        nrows = 10
        ptbl = petl.dummytable(numrows=nrows)
        tbl = Table(ptbl)
        assert tbl.num_rows == nrows

    def test_from_invalid_list(self):
        # Tests that a table can't be created from a list of invalid items
        list_of_invalid = [1, 2, 3]
        with pytest.raises(ValueError, match="Could not create Table"):
            Table(list_of_invalid)

    def test_from_empty_petl(self):
        # This test ensures that this would fail: Table(None)
        # Even while allowing Table() to work
        with pytest.raises(ValueError, match="Could not initialize table from input type"):
            Table(None)

    def test_from_empty_list(self):
        # Just ensure this doesn't throw an error
        Table()
        Table([])
        Table([[]])

    def test_materialize(self):
        # Simple test that materializing doesn't change the table
        tbl_materialized = Table(self.lst_dicts)
        tbl_materialized.materialize()

        assert_matching_tables(self.tbl, tbl_materialized)

    def test_materialize_to_file(self):
        # Simple test that materializing doesn't change the table
        tbl_materialized = Table(self.lst_dicts)
        _ = tbl_materialized.materialize_to_file()

        assert_matching_tables(self.tbl, tbl_materialized)

    def test_empty_column(self):
        # Test that returns True on an empty column and False on a populated one.

        tbl = Table([["a", "b"], ["1", None], ["2", None]])

        assert tbl.empty_column("b")
        assert not tbl.empty_column("a")

    def test_from_columns(self):
        header = ["col1", "col2"]
        col1 = [1, 2, 3]
        col2 = ["a", "b", "c"]
        tbl = Table.from_columns([col1, col2], header=header)

        assert tbl[0] == {"col1": 1, "col2": "a"}

    # Removing this test since it is an optional dependency.
    """
    def test_from_datafame(self):

        import pandas

        # Assert creates table without index
        tbl = Table(self.lst)
        tbl_from_df = Table.from_dataframe(tbl.to_dataframe())
        assert_matching_tables(tbl, tbl_from_df)


    def test_to_dataframe(self):

        # Is a dataframe
        self.assertIsInstance(self.tbl.to_dataframe(), pandas.core.frame.DataFrame)
    """

    def test_to_petl(self):
        # Is a petl table
        assert isinstance(self.tbl.to_petl(), petl.io.json.DictsView)

    def test_to_html(self):
        html_file = str(Path(self.tmp_folder) / "test.html")

        # Test writing file
        self.tbl.to_html(html_file)

        # Test written correctly
        html = (
            "<table class='petl'>\n"
            "<thead>\n"
            "<tr>\n"
            "<th>first</th>\n"
            "<th>last</th>\n"
            "</tr>\n"
            "</thead>\n"
            "<tbody>\n"
            "<tr>\n"
            "<td>Bob</td>\n"
            "<td>Smith</td>\n"
            "</tr>\n"
            "</tbody>\n"
            "</table>\n"
        )
        assert Path(html_file).read_text() == html

    def test_to_temp_html(self):
        # Test write to object
        path = Path(self.tbl.to_html())

        # Written correctly
        html = (
            "<table class='petl'>\n"
            "<thead>\n"
            "<tr>\n"
            "<th>first</th>\n"
            "<th>last</th>\n"
            "</tr>\n"
            "</thead>\n"
            "<tbody>\n"
            "<tr>\n"
            "<td>Bob</td>\n"
            "<td>Smith</td>\n"
            "</tr>\n"
            "</tbody>\n"
            "</table>\n"
        )
        assert path.read_text() == html

    def test_to_avro_basic(self):
        # Create a temporary directory and file
        with tempfile.TemporaryDirectory() as temp_dir:
            avro_file = Path(temp_dir) / "test.avro"

            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

            # Test basic functionality
            tbl.to_avro(avro_file)

            # Verify the file exists
            assert Path.exists(avro_file)

            # Read it back and verify content
            result_tbl = Table.from_avro(avro_file)
            assert len(result_tbl) == len(tbl)
            assert sorted(result_tbl.columns) == sorted(tbl.columns)

            # Check data values match
            for i in range(len(tbl)):
                for col in tbl.columns:
                    assert result_tbl[i][col] == tbl[i][col]

    def test_to_avro_with_schema(self):
        # Create a temporary directory and file
        with tempfile.TemporaryDirectory() as temp_dir:
            avro_file = Path(temp_dir) / "test.avro"

            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

            # Test with explicit schema
            schema = {
                "doc": "Some people records.",
                "name": "People",
                "namespace": "test",
                "type": "record",
                "fields": [
                    {"name": "first", "type": "string"},
                    {"name": "last", "type": "string"},
                ],
            }

            tbl.to_avro(avro_file, schema=schema)

            # Read it back and verify content
            result_tbl = Table.from_avro(avro_file)
            assert len(result_tbl) == len(tbl)
            assert sorted(result_tbl.columns) == sorted(tbl.columns)

    def test_to_avro_different_codecs(self):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

            # Test with different compression codecs
            for codec in ["null", "deflate", "bzip2"]:
                test_file = Path(temp_dir) / f"test_{codec}.avro"
                tbl.to_avro(test_file, codec=codec)

                # Verify the file exists
                assert Path.exists(test_file)

                # Read it back and verify content
                result_tbl = Table.from_avro(test_file)
                assert len(result_tbl) == len(tbl)
                assert sorted(result_tbl.columns) == sorted(tbl.columns)

    def test_to_avro_with_compression_level(self):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

            # Test with compression level
            codec = "deflate"
            for level in [1, 5, 9]:
                test_file = Path(temp_dir) / f"test_level_{level}.avro"
                tbl.to_avro(test_file, codec=codec, compression_level=level)

                # Verify the file exists
                assert Path.exists(test_file)

                # Read it back and verify content
                result_tbl = Table.from_avro(test_file)
                assert len(result_tbl) == len(tbl)

    def test_to_avro_sample_size(self):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

            # Test with different sample sizes for schema inference
            for sample in [1, 5, 10]:
                test_file = Path(temp_dir) / f"test_sample_{sample}.avro"
                tbl.to_avro(test_file, sample=sample)

                # Verify the file exists
                assert Path.exists(test_file)

                # Read it back and verify content
                result_tbl = Table.from_avro(test_file)
                assert len(result_tbl) == len(tbl)

    def test_to_avro_with_avro_args(self):
        # Create a temporary directory and file
        with tempfile.TemporaryDirectory() as temp_dir:
            avro_file = Path(temp_dir) / "test.avro"

            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

            # Test with additional arguments to fastavro
            tbl.to_avro(
                avro_file,
                sync_interval=16000,  # Custom sync marker interval
                metadata={"created_by": "parsons_test"},
            )

            # Verify the file exists
            assert Path.exists(avro_file)

            # Read it back and verify content
            result_tbl = Table.from_avro(avro_file)
            assert len(result_tbl) == len(tbl)

    def test_to_avro_complex_types(self):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with more complex data types
            complex_data = [
                {
                    "name": "Bob",
                    "tags": ["tag1", "tag2"],
                    "metadata": {"city": "NYC", "state": "NY"},
                },
                {"name": "Jim", "tags": ["tag3"], "metadata": {"city": "LA", "state": "CA"}},
            ]
            complex_tbl = Table(complex_data)

            test_file = Path(temp_dir) / "test_complex.avro"
            complex_tbl.to_avro(test_file)

            # Verify the file exists
            assert Path.exists(test_file)

            # Read it back and verify content
            result_tbl = Table.from_avro(test_file)
            assert len(result_tbl) == len(complex_tbl)

    def _assert_expected_csv(self, path, orig_tbl):
        result_tbl = Table.from_csv(path)
        assert_matching_tables(orig_tbl, result_tbl)

    def test_to_from_csv(self):
        with TemporaryDirectory() as tempdir:
            path = str(Path(tempdir) / "test.csv")
            self.tbl.to_csv(path)
            self._assert_expected_csv(path, self.tbl)

    def test_to_from_csv_compressed(self):
        with TemporaryDirectory() as tempdir:
            path = str(Path(tempdir) / "test.csv.gz")
            self.tbl.to_csv(path)
            self._assert_expected_csv(path, self.tbl)

    def test_to_from_temp_csv(self):
        path = self.tbl.to_csv()
        self._assert_expected_csv(path, self.tbl)

    def test_to_from_temp_csv_compressed(self):
        path = self.tbl.to_csv(temp_file_compression="gzip")
        self._assert_expected_csv(path, self.tbl)

    def test_from_csv_string(self):
        path = self.tbl.to_csv()
        # Pull the file into a string
        csv_string = Path(path).read_text()

        result_tbl = Table.from_csv_string(csv_string)
        assert_matching_tables(self.tbl, result_tbl)

    def test_append_csv_compressed(self):
        path = self.tbl.to_csv(temp_file_compression="gzip")
        append_tbl = Table([{"first": "Mary", "last": "Nichols"}])
        append_tbl.append_csv(path)

        result_tbl = Table.from_csv(path)
        # Combine tables, so we can check the resulting file
        self.tbl.concat(append_tbl)
        assert_matching_tables(self.tbl, result_tbl)

    def test_from_csv_raises_on_empty_file(self):
        # Create empty file
        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "empty.csv"
            path.open(mode="a").close()

            assert pytest.raises(ValueError, Table.from_csv, str(path))

    def test_to_csv_zip(self):
        my_zip = "myzip.zip"
        try:
            # Test using the to_csv() method
            self.tbl.to_csv(my_zip)
            tmp = zip_archive.unzip_archive(my_zip)
            assert_matching_tables(self.tbl, Table.from_csv(tmp))

            # Test using the to_csv_zip() method
            self.tbl.to_zip_csv(my_zip)
            tmp = zip_archive.unzip_archive(my_zip)
            assert_matching_tables(self.tbl, Table.from_csv(tmp))
        finally:
            Path(my_zip).unlink()

    def test_to_civis(self):
        # Not really sure the best way to do this at the moment.
        pass

    def test_to_from_json(self):
        with TemporaryDirectory() as tempdir:
            path = str(Path(tempdir) / "test.json")
            self.tbl.to_json(path)

            result_tbl = Table.from_json(path)
            assert_matching_tables(self.tbl, result_tbl)

    def test_to_from_json_compressed(self):
        with TemporaryDirectory() as tempdir:
            path = str(Path(tempdir) / "test.json.gz")
            self.tbl.to_json(path)

            result_tbl = Table.from_json(path)
            assert_matching_tables(self.tbl, result_tbl)

    def test_to_from_temp_json(self):
        path = self.tbl.to_json()
        result_tbl = Table.from_json(path)
        assert_matching_tables(self.tbl, result_tbl)

    def test_to_from_temp_json_compressed(self):
        path = self.tbl.to_json(temp_file_compression="gzip")
        result_tbl = Table.from_json(path)
        assert_matching_tables(self.tbl, result_tbl)

    def test_to_from_json_line_delimited(self):
        with TemporaryDirectory() as tempdir:
            path = str(Path(tempdir) / "test.json")
            self.tbl.to_json(path, line_delimited=True)

            result_tbl = Table.from_json(path, line_delimited=True)
            assert_matching_tables(self.tbl, result_tbl)

    def test_to_from_json_line_delimited_compressed(self):
        with TemporaryDirectory() as tempdir:
            path = str(Path(tempdir) / "test.json.gz")
            self.tbl.to_json(path, line_delimited=True)

            result_tbl = Table.from_json(path, line_delimited=True)
            assert_matching_tables(self.tbl, result_tbl)

    def test_columns(self):
        # Test that columns are listed correctly
        assert self.tbl.columns == ["first", "last"]

    def test_add_column(self):
        # Test that a new column is added correctly
        self.tbl.add_column("middle", index=1)
        assert self.tbl.columns[1] == "middle"

    def test_column_add_dupe(self):
        # Test that we can't add an existing column name
        column = "first"
        with pytest.raises(ValueError, match=f"Column {column} already exists"):
            self.tbl.add_column(column)

    def test_add_column_if_exists(self):
        self.tbl.add_column("first", if_exists="replace")
        assert self.tbl.columns == ["first", "last"]

    def test_remove_column(self):
        # Test that column is removed correctly
        self.tbl.remove_column("first")
        assert self.tbl.data[0] != "first"

    def test_rename_column(self):
        # Test that you can rename a column
        self.tbl.rename_column("first", "f")
        assert self.tbl.columns[0] == "f"

    def test_column_rename_dupe(self):
        # Test that we can't rename to a column that already exists
        with pytest.raises(ValueError, match="Column first already exists"):
            self.tbl.rename_column("last", "first")

    def test_rename_columns(self):
        # Test renaming columns with a valid column_map
        column_map = {"first": "firstname", "last": "lastname"}
        self.tbl.rename_columns(column_map)
        assert self.tbl.columns == ["firstname", "lastname"]

    def test_rename_columns_partial(self):
        # Test renaming only some columns
        column_map = {"first": "firstname"}
        self.tbl.rename_columns(column_map)
        assert self.tbl.columns == ["firstname", "last"]

    def test_rename_columns_nonexistent(self):
        # Test renaming a column that doesn't exist
        column_map = {"nonexistent": "newname"}
        with pytest.raises(
            KeyError, match=f"Column name {next(iter(column_map.keys()))} does not exist"
        ):
            self.tbl.rename_columns(column_map)

    def test_rename_columns_empty(self):
        # Test renaming with an empty column_map
        column_map = {}
        self.tbl.rename_columns(column_map)
        assert self.tbl.columns == ["first", "last"]

    def test_rename_columns_duplicate(self):
        # Test renaming to a column name that already exists
        column_map = {"first": "last"}
        with pytest.raises(
            ValueError,
            match=f"Column name {column_map[next(iter(column_map.keys()))]} already exists",
        ):
            self.tbl.rename_columns(column_map)

    def test_fill_column(self):
        # Test that the column is filled
        tbl = Table(self.lst)

        # Fixed Value
        tbl.fill_column("c", 0)
        assert list(tbl.table["c"]) == [0] * tbl.num_rows

        # Calculated Value
        tbl.fill_column("c", lambda x: x["b"] * 2)
        assert list(tbl.table["c"]) == [x["b"] * 2 for x in self.lst]

    def test_fillna_column(self):
        # Test that None values in the column are filled

        self.lst = [
            {"a": 1, "b": 2, "c": 3},
            {"a": 4, "b": 5, "c": None},
            {"a": 7, "b": 8, "c": 9},
            {"a": 10, "b": 11, "c": None},
            {"a": 13, "b": 14, "c": 15},
        ]

        # Fixed Value only
        tbl = Table(self.lst)
        tbl.fillna_column("c", 0)
        assert list(tbl.table["c"]) == [3, 0, 9, 0, 15]

    def test_move_column(self):
        # Test moving a column from end to front
        self.tbl.move_column("last", 0)
        assert self.tbl.columns[0] == "last"

    def test_convert_column(self):
        # Test that column updates
        self.tbl.convert_column("first", "upper")
        assert self.tbl[0] == {"first": "BOB", "last": "Smith"}

    def test_convert_columns_to_str(self):
        # Test that all columns are string
        mixed_raw = [
            {"col1": 1, "col2": 2, "col3": 3},
            {"col1": "one", "col2": 2, "col3": [3, "three", 3.0]},
            {"col1": {"one": 1, "two": 2.0}, "col2": None, "col3": "three"},
        ]
        tbl = Table(mixed_raw)
        tbl.convert_columns_to_str()

        cols = tbl.get_columns_type_stats()
        type_set = {i for x in cols for i in x["type"]}
        assert "str" in type_set
        assert len(type_set) == 1

    def test_convert_table(self):
        # Test that the table updates
        self.tbl.convert_table("upper")
        assert self.tbl[0] == {"first": "BOB", "last": "SMITH"}

    def test_coalesce_columns(self):
        # Test coalescing into an existing column
        test_raw = [
            {"first": "Bob", "last": "Smith", "lastname": None},
            {"first": "Jane", "last": "", "lastname": "Doe"},
            {"first": "Mary", "last": "Simpson", "lastname": "Peters"},
        ]
        tbl = Table(test_raw)
        tbl.coalesce_columns("last", ["last", "lastname"])

        expected = Table(
            [
                {"first": "Bob", "last": "Smith"},
                {"first": "Jane", "last": "Doe"},
                {"first": "Mary", "last": "Simpson"},
            ]
        )
        assert_matching_tables(tbl, expected)

        # Test coalescing into a new column
        tbl = Table(test_raw)
        tbl.coalesce_columns("new_last", ["last", "lastname"])
        expected = Table(
            [
                {"first": "Bob", "new_last": "Smith"},
                {"first": "Jane", "new_last": "Doe"},
                {"first": "Mary", "new_last": "Simpson"},
            ]
        )
        assert_matching_tables(tbl, expected)

    def test_unpack_dict(self):
        test_dict = [{"a": 1, "b": {"nest1": 1, "nest2": 2}}]
        test_table = Table(test_dict)

        # Test that dict at the top level
        test_table.unpack_dict("b", prepend=False)
        assert test_table.columns == ["a", "nest1", "nest2"]

    def test_unpack_list(self):
        test_table = Table([{"a": 1, "b": [1, 2, 3]}])

        # Test that list at the top level
        test_table.unpack_list("b", replace=True)
        assert test_table.columns == ["a", "b_0", "b_1", "b_2"]

    def test_unpack_list_with_mixed_col(self):
        # Test unpacking column with non-list items
        mixed_tbl = Table([{"id": 1, "tag": [1, 2, None, 4]}, {"id": 2, "tag": None}])
        tbl_unpacked = Table(mixed_tbl.unpack_list("tag"))

        # Make sure result has the right number of columns
        assert len(tbl_unpacked.columns) == 5

        result_table = Table(
            [
                {"id": 1, "tag_0": 1, "tag_1": 2, "tag_2": None, "tag_3": 4},
                {"id": 2, "tag_0": None, "tag_1": None, "tag_2": None, "tag_3": None},
            ]
        )

        # Check that the values for both rows are distributed correctly
        assert (
            result_table.data[0] + result_table.data[1]
            == tbl_unpacked.data[0] + tbl_unpacked.data[1]
        )

    def test_unpack_nested_columns_as_rows(self):
        # A Table with mixed content
        test_table = Table(
            [
                {"id": 1, "nested": {"A": 1, "B": 2, "C": 3}, "extra": "hi"},
                {"id": 2, "nested": {"A": 4, "B": 5, "I": 6}, "extra": "hi"},
                {"id": 3, "nested": "string!", "extra": "hi"},
                {"id": 4, "nested": None, "extra": "hi"},
                {"id": 5, "nested": ["this!", "is!", "a!", "list!"], "extra": "hi"},
            ]
        )

        standalone = test_table.unpack_nested_columns_as_rows("nested")

        # Check that the columns are as expected
        assert standalone.columns == ["uid", "id", "nested", "value"]

        # Check that the row count is as expected
        assert standalone.num_rows == 11

        # Check that the uids are unique, indicating that each row is unique
        assert len({row["uid"] for row in standalone}) == 11

    def test_unpack_nested_columns_as_rows_expanded(self):
        test_table = Table(
            [
                {"id": 1, "nested": {"A": 1, "B": 2, "C": 3}, "extra": "hi"},
                {"id": 2, "nested": {"A": 4, "B": 5, "I": 6}, "extra": "hi"},
                {"id": 3, "nested": "string!", "extra": "hi"},
                {"id": 4, "nested": None, "extra": "hi"},
                {"id": 5, "nested": ["this!", "is!", "a!", "list!"], "extra": "hi"},
            ]
        )

        expanded = test_table.unpack_nested_columns_as_rows("nested", expand_original=True)

        # Check that the columns are as expected
        assert expanded.columns == ["uid", "id", "extra", "nested", "nested_value"]

        # Check that the row count is as expected
        assert expanded.num_rows == 12

        # Check that the uids are unique, indicating that each row is unique
        assert len({row["uid"] for row in expanded}) == 12

    def test_cut(self):
        # Test that the cut works correctly
        cut_tbl = self.tbl.cut("first")
        assert cut_tbl.columns == ["first"]

    def test_row_select(self):
        tbl = Table([["foo", "bar", "baz"], ["c", 4, 9.3], ["a", 2, 88.2], ["b", 1, 23.3]])
        expected = Table([{"foo": "a", "bar": 2, "baz": 88.2}])

        # Try with this method
        select_tbl = tbl.select_rows("{foo} == 'a' and {baz} > 88.1")
        assert select_tbl.data[0] == expected.data[0]

        # And try with this method
        select_tbl2 = tbl.select_rows(lambda row: row.foo == "a" and row.baz > 88.1)
        assert select_tbl2.data[0] == expected.data[0]

    def test_remove_null_rows(self):
        # Test that null rows are removed from a single column
        null_table = Table([{"a": 1, "b": 2}, {"a": 1, "b": None}])
        assert null_table.remove_null_rows("b").num_rows == 1

        # Teest that null rows are removed from multiple columns
        null_table = Table([{"a": 1, "b": 2, "c": 3}, {"a": 1, "b": None, "c": 3}])
        assert null_table.remove_null_rows(["b", "c"]).num_rows == 1

    def test_long_table(self):
        # Create a long table, that is 4 rows long
        tbl = Table([{"id": 1, "tag": [1, 2, 3, 4]}])
        assert tbl.long_table(["id"], "tag").num_rows == 4

        # Assert that column has been dropped
        assert tbl.columns == ["id"]

        # Assert that column has been retained
        tbl_keep = Table([{"id": 1, "tag": [1, 2, 3, 4]}])
        tbl_keep.long_table(["id"], "tag", retain_original=True)
        assert tbl_keep.columns == ["id", "tag"]

    def test_long_table_with_na(self):
        # Create a long table that is 4 rows long
        tbl = Table([{"id": 1, "tag": [1, 2, 3, 4]}, {"id": 2, "tag": None}])
        assert tbl.long_table(["id"], "tag").num_rows == 4

        # Assert that column has been dropped
        assert tbl.columns == ["id"]

        # Assert that column has been retained
        tbl_keep = Table([{"id": 1, "tag": [1, 2, 3, 4]}, {"id": 2, "tag": None}])
        tbl_keep.long_table(["id"], "tag", retain_original=True)
        assert tbl_keep.columns == ["id", "tag"]

    def test_rows(self):
        # Test that there is only one row in the table
        assert self.tbl.num_rows == 1

    def test_first(self):
        # Test that the first value in the table is returned.
        assert self.tbl.first == "Bob"

        # Test empty value returns None
        empty_tbl = Table([[1], [], [3]])
        assert empty_tbl.first is None

    def test_get_item(self):
        # Test indexing on table

        # Test a valid column
        tbl = Table(self.lst)
        lst = [1, 4, 7, 10, 13]
        assert tbl["a"] == lst

        # Test a valid row
        row = {"a": 4, "b": 5, "c": 6}
        assert tbl[1] == row

    def test_column_data(self):
        # Test that that the data in the column is returned as a list

        # Test a valid column
        tbl = Table(self.lst)
        lst = [1, 4, 7, 10, 13]
        assert tbl.column_data("a") == lst

        # Test an invalid column
        with pytest.raises(ValueError, match="Column name not found."):
            tbl.column_data("d")

    def test_row_data(self):
        # Test a valid column
        tbl = Table(self.lst)
        row = {"a": 4, "b": 5, "c": 6}
        assert tbl.row_data(1) == row

    def test_stack(self):
        tbl1 = self.tbl.select_rows(lambda x: x)
        tbl2 = Table([{"first": "Mary", "last": "Nichols"}])
        # Different column names shouldn't matter for stack()
        tbl3 = Table([{"f": "Lucy", "l": "Peterson"}])
        tbl1.stack(tbl2, tbl3)

        expected_tbl = Table(petl.stack(self.tbl.table, tbl2.table, tbl3.table))
        assert_matching_tables(expected_tbl, tbl1)

    def test_concat(self):
        tbl1 = self.tbl.select_rows(lambda x: x)
        tbl2 = Table([{"first": "Mary", "last": "Nichols"}])
        tbl3 = Table([{"first": "Lucy", "last": "Peterson"}])
        tbl1.concat(tbl2, tbl3)

        expected_tbl = Table(petl.cat(self.tbl.table, tbl2.table, tbl3.table))
        assert_matching_tables(expected_tbl, tbl1)

    def test_chunk(self):
        test_table = Table(petl.randomtable(3, 499, seed=42))
        chunks = test_table.chunk(100)

        # Assert rows of each is 100
        for c in chunks[:3]:
            assert c.num_rows == 100

        # Assert last table is 99
        assert chunks[4].num_rows == 99

    def test_match_columns(self):
        raw = [
            {"first name": "Mary", "LASTNAME": "Nichols", "Middle__Name": "D"},
            {"first name": "Lucy", "LASTNAME": "Peterson", "Middle__Name": "S"},
        ]
        tbl = Table(raw)

        desired_raw = [
            {"first_name": "Mary", "middle_name": "D", "last_name": "Nichols"},
            {"first_name": "Lucy", "middle_name": "S", "last_name": "Peterson"},
        ]
        desired_tbl = Table(desired_raw)

        # Test with fuzzy matching
        tbl.match_columns(desired_tbl.columns)
        assert_matching_tables(desired_tbl, tbl)

        # Test disable fuzzy matching, and fail due due to the missing cols
        with pytest.raises(TypeError, match="Table is missing column"):
            Table(raw).match_columns(
                desired_tbl.columns,
                fuzzy_match=False,
                if_missing_columns="fail",
            )

        # Test disable fuzzy matching, and fail due to the extra cols
        with pytest.raises(TypeError, match="Table has extra column"):
            Table(raw).match_columns(
                desired_tbl.columns,
                fuzzy_match=False,
                if_extra_columns="fail",
            )

        # Test table that already has the right columns, shouldn't need fuzzy match
        tbl = Table(desired_raw)
        tbl.match_columns(
            desired_tbl.columns,
            fuzzy_match=False,
            if_missing_columns="fail",
            if_extra_columns="fail",
        )
        assert_matching_tables(desired_tbl, tbl)

        # Test table with missing col, verify the missing col gets added by default
        tbl = Table(
            [
                {"first name": "Mary", "LASTNAME": "Nichols"},
                {"first name": "Lucy", "LASTNAME": "Peterson"},
            ]
        )
        tbl.match_columns(desired_tbl.columns)
        desired_tbl = (
            Table(desired_raw).remove_column("middle_name").add_column("middle_name", index=1)
        )
        assert_matching_tables(desired_tbl, tbl)

        # Test table with extra col, verify the extra col gets removed by default
        tbl = Table(
            [
                {
                    "first name": "Mary",
                    "LASTNAME": "Nichols",
                    "Age": 32,
                    "Middle__Name": "D",
                },
                {
                    "first name": "Lucy",
                    "LASTNAME": "Peterson",
                    "Age": 26,
                    "Middle__Name": "S",
                },
            ]
        )
        desired_tbl = Table(desired_raw)
        tbl.match_columns(desired_tbl.columns)
        assert_matching_tables(desired_tbl, tbl)

        # Test table with two columns that normalize the same and aren't in desired cols, verify
        # they both get removed.
        tbl = Table(
            [
                {
                    "first name": "Mary",
                    "LASTNAME": "Nichols",
                    "Age": 32,
                    "Middle__Name": "D",
                    "AGE": None,
                },
                {
                    "first name": "Lucy",
                    "LASTNAME": "Peterson",
                    "Age": 26,
                    "Middle__Name": "S",
                    "AGE": None,
                },
            ]
        )
        tbl.match_columns(desired_tbl.columns)
        assert_matching_tables(desired_tbl, tbl)

        # Test table with two columns that match desired cols, verify only the first gets kept.
        tbl = Table(
            [
                {
                    "first name": "Mary",
                    "LASTNAME": "Nichols",
                    "First Name": None,
                    "Middle__Name": "D",
                },
                {
                    "first name": "Lucy",
                    "LASTNAME": "Peterson",
                    "First Name": None,
                    "Middle__Name": "S",
                },
            ]
        )
        tbl.match_columns(desired_tbl.columns)
        assert_matching_tables(desired_tbl, tbl)

    def test_to_dicts(self):
        assert self.lst == Table(self.lst).to_dicts()
        assert self.lst_dicts == self.tbl.to_dicts()

    def test_reduce_rows(self):
        table = [
            ["foo", "bar"],
            ["a", 3],
            ["a", 7],
            ["b", 2],
            ["b", 1],
            ["b", 9],
            ["c", 4],
        ]
        expected = [
            {"foo": "a", "barsum": 10},
            {"foo": "b", "barsum": 12},
            {"foo": "c", "barsum": 4},
        ]

        ptable = Table(table)

        ptable.reduce_rows(
            "foo",
            lambda key, rows: [key, sum(row[1] for row in rows)],
            ["foo", "barsum"],
        )

        assert expected == ptable.to_dicts()

    def test_map_columns_exact(self):
        input_tbl = Table([["fn", "ln", "MID"], ["J", "B", "H"]])

        column_map = {
            "first_name": ["fn", "first"],
            "last_name": ["last", "ln"],
            "middle_name": ["mi"],
        }

        exact_tbl = Table([["first_name", "last_name", "MID"], ["J", "B", "H"]])
        input_tbl.map_columns(column_map)
        assert_matching_tables(input_tbl, exact_tbl)

    def test_map_columns_fuzzy(self):
        input_tbl = Table([["fn", "ln", "Mi_"], ["J", "B", "H"]])

        column_map = {
            "first_name": ["fn", "first"],
            "last_name": ["last", "ln"],
            "middle_name": ["mi"],
        }

        fuzzy_tbl = Table([["first_name", "last_name", "middle_name"], ["J", "B", "H"]])
        input_tbl.map_columns(column_map, exact_match=False)
        assert_matching_tables(input_tbl, fuzzy_tbl)

    def test_get_column_max_with(self):
        tbl = Table(
            [
                ["a", "b", "c"],
                ["wide_text", False, "slightly longer text"],
                ["text", 2, "byte_text🏽‍⚕️✊🏽🤩"],
            ]
        )

        # Basic test
        assert tbl.get_column_max_width("a") == 9

        # Doesn't break for non-strings
        assert tbl.get_column_max_width("b") == 5

        # Evaluates based on byte length rather than char length
        assert tbl.get_column_max_width("c") == 33

    def test_sort(self):
        # Test basic sort
        unsorted_tbl = Table([["a", "b"], [3, 1], [2, 2], [1, 3]])
        sorted_tbl = unsorted_tbl.sort()
        assert sorted_tbl[0] == {"a": 1, "b": 3}

        # Test column sort
        unsorted_tbl = Table([["a", "b"], [3, 1], [2, 2], [1, 3]])
        sorted_tbl = unsorted_tbl.sort("b")
        assert sorted_tbl[0] == {"a": 3, "b": 1}

        # Test reverse sort
        unsorted_tbl = Table([["a", "b"], [3, 1], [2, 2], [1, 3]])
        sorted_tbl = unsorted_tbl.sort(reverse=True)
        assert sorted_tbl[0] == {"a": 3, "b": 1}

    def test_set_header(self):
        # Rename columns
        tbl = Table([["one", "two"], [1, 2], [3, 4]])
        new_tbl = tbl.set_header(["oneone", "twotwo"])

        assert new_tbl[0] == {"oneone": 1, "twotwo": 2}

        # Change number of columns
        tbl = Table([["one", "two"], [1, 2], [3, 4]])
        new_tbl = tbl.set_header(["one"])

        assert new_tbl[0] == {"one": 1}

    def test_bool(self):
        empty = Table()
        not_empty = Table([{"one": 1, "two": 2}])

        assert not empty
        assert not_empty

    def test_use_petl(self):
        # confirm that this method doesn't exist for parsons.Table
        with pytest.raises(AttributeError):
            Table.skipcomments  # noqa: B018

        tbl = Table(
            [
                ["col1", "col2"],
                [
                    "# this is a comment row",
                ],
                ["a", 1],
                ["#this is another comment", "this is also ignored"],
                ["b", 2],
            ]
        )
        tbl_expected = Table([["col1", "col2"], ["a", 1], ["b", 2]])

        tbl_after = tbl.use_petl("skipcomments", "#")
        assert_matching_tables(tbl_expected, tbl_after)

        tbl.use_petl("skipcomments", "#", update_table=True)
        assert_matching_tables(tbl_expected, tbl)

        from petl.util.base import Table as PetlTable

        tbl_petl = tbl.use_petl("skipcomments", "#", to_petl=True)
        assert isinstance(tbl_petl, PetlTable)

    def test_deduplicate(self):
        # Confirm deduplicate works with no keys for one-column duplicates
        tbl = Table([["a"], [1], [2], [2], [3]])
        tbl_expected = Table([["a"], [1], [2], [3]])
        tbl.deduplicate()
        assert_matching_tables(tbl_expected, tbl)

        # Confirm deduplicate works with no keys for multiple columns
        tbl = Table([["a", "b"], [1, 2], [1, 2], [1, 3], [2, 3]])
        tbl_expected = Table(
            [
                ["a", "b"],
                [1, 2],
                [1, 3],
                [2, 3],
            ]
        )
        tbl.deduplicate()
        assert_matching_tables(tbl_expected, tbl)

        # Confirm deduplicate works with one key for multiple columns
        tbl = Table([["a", "b"], [1, 3], [1, 2], [1, 2], [2, 3]])
        tbl_expected = Table(
            [
                ["a", "b"],
                [1, 3],
                [2, 3],
            ]
        )
        tbl.deduplicate(keys=["a"])
        assert_matching_tables(tbl_expected, tbl)

        # Confirm sorting deduplicate works with one key for multiple columns

        # Note that petl sorts on the column(s) you're deduping on
        # Meaning it will ignore the 'b' column below
        # That is, the first row, [1,3],
        # would not get moved to after the [1,2]
        tbl = Table([["a", "b"], [2, 3], [1, 3], [1, 2], [1, 2]])
        tbl_expected = Table(
            [
                ["a", "b"],
                [1, 3],
                [2, 3],
            ]
        )
        tbl.deduplicate(keys=["a"], presorted=False)
        assert_matching_tables(tbl_expected, tbl)

        # Confirm sorting deduplicate works for two of two columns
        tbl = Table([["a", "b"], [2, 3], [1, 3], [1, 2], [1, 2]])
        tbl_expected = Table(
            [
                ["a", "b"],
                [1, 2],
                [1, 3],
                [2, 3],
            ]
        )
        tbl.deduplicate(keys=["a", "b"], presorted=False)
        assert_matching_tables(tbl_expected, tbl)

        # Confirm deduplicate works for multiple keys
        tbl = Table([["a", "b", "c"], [1, 2, 3], [1, 2, 3], [1, 2, 4], [1, 3, 2], [2, 3, 4]])
        tbl_expected = Table([["a", "b", "c"], [1, 2, 3], [1, 3, 2], [2, 3, 4]])
        tbl.deduplicate(["a", "b"])
        assert_matching_tables(tbl_expected, tbl)

    def test_head(self):
        tbl = Table([["a", "b"], [1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])
        tbl_expected = Table([["a", "b"], [1, 2], [3, 4]])
        tbl.head(2)
        assert_matching_tables(tbl_expected, tbl)

    def test_tail(self):
        tbl = Table([["a", "b"], [1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])
        tbl_expected = Table([["a", "b"], [7, 8], [9, 10]])
        tbl.tail(2)
        assert_matching_tables(tbl_expected, tbl)
