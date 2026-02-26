from pathlib import Path
from typing import Any

import petl
import pytest

from parsons import Table
from parsons.utilities import zip_archive
from test.conftest import assert_matching_tables

# Notes :
# - The `Table.to_postgres()` test is housed in the Postgres tests
# - The `Table.from_postgres()` test is housed in the Postgres tests
# - The `Table.to_dataframe()` test is housed in the pandas test folder
# - The `Table.from_dataframe()` test is housed in the pandas test folder
# - The `Table.to_avro()` test is housed in the avro test folder
# - The `Table.from_avro()` test is housed in the avro test folder


# Tests for creating Table objects from various sources
class TestTableCreation:
    """Tests for creating Table objects from various sources"""

    def test_from_list_of_dicts(self, sample_data):
        tbl = Table(sample_data["lst"])

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

    @pytest.mark.parametrize(
        "input_data",
        [
            [],
            [[]],
            None,  # This represents Table() with no args
        ],
        ids=["empty_list", "list_with_empty_list", "no_args"],
    )
    def test_from_empty_list(self, input_data):
        # Just ensure this doesn't throw an error
        Table() if not input_data else Table(input_data)

    def test_from_columns(self):
        header = ["col1", "col2"]
        col1 = [1, 2, 3]
        col2 = ["a", "b", "c"]
        tbl = Table.from_columns([col1, col2], header=header)

        assert tbl[0] == {"col1": 1, "col2": "a"}

    def test_materialize(self, tbl, sample_data):
        # Simple test that materializing doesn't change the table
        tbl_materialized = Table(sample_data["lst_dicts"])
        tbl_materialized.materialize()

        assert_matching_tables(tbl, tbl_materialized)

    def test_materialize_to_file(self, tbl, sample_data):
        # Simple test that materializing doesn't change the table
        tbl_materialized = Table(sample_data["lst_dicts"])
        _ = tbl_materialized.materialize_to_file()

        assert_matching_tables(tbl, tbl_materialized)


class TestFileOperations:
    """Tests for CSV, JSON, HTML, and other file operations"""

    def _assert_expected_csv(self, path, orig_tbl):
        result_tbl = Table.from_csv(path)
        assert_matching_tables(orig_tbl, result_tbl)

    @pytest.mark.parametrize(
        ("filename", "compression"),
        [
            ("test.csv", None),
            ("test.csv.gz", "gzip"),
        ],
        ids=["uncompressed", "compressed"],
    )
    def test_to_from_csv(self, tbl, tmp_path, filename, compression):
        path = str(tmp_path / filename)
        tbl.to_csv(path)
        self._assert_expected_csv(path, tbl)

    @pytest.mark.parametrize("compression", [None, "gzip"], ids=["uncompressed", "compressed"])
    def test_to_from_temp_csv(self, tbl, compression):
        path = tbl.to_csv(temp_file_compression=compression) if compression else tbl.to_csv()
        self._assert_expected_csv(path, tbl)

    def test_from_csv_string(self, tbl):
        path = tbl.to_csv()
        # Pull the file into a string
        csv_string = Path(path).read_text()

        result_tbl = Table.from_csv_string(csv_string)
        assert_matching_tables(tbl, result_tbl)

    def test_append_csv_compressed(self, tbl):
        path = tbl.to_csv(temp_file_compression="gzip")
        append_tbl = Table([{"first": "Mary", "last": "Nichols"}])
        append_tbl.append_csv(path)

        result_tbl = Table.from_csv(path)
        # Combine tables, so we can check the resulting file
        tbl.concat(append_tbl)
        assert_matching_tables(tbl, result_tbl)

    def test_from_csv_raises_on_empty_file(self, tmp_path: Path):
        # Create empty file
        path = tmp_path / "empty.csv"
        path.touch()

        with pytest.raises(ValueError, match="CSV file is empty"):
            Table.from_csv(str(path))

    def test_to_csv_zip(self, tbl):
        my_zip = "myzip.zip"
        try:
            # Test using the to_csv() method
            tbl.to_csv(my_zip)
            tmp = zip_archive.unzip_archive(my_zip)
            assert_matching_tables(tbl, Table.from_csv(tmp))

            # Test using the to_csv_zip() method
            tbl.to_zip_csv(my_zip)
            tmp = zip_archive.unzip_archive(my_zip)
            assert_matching_tables(tbl, Table.from_csv(tmp))
        finally:
            Path(my_zip).unlink()

    @pytest.mark.parametrize(
        ("filename", "compression"),
        [
            ("test.json", None),
            ("test.json.gz", "gzip"),
        ],
        ids=["uncompressed", "compressed"],
    )
    def test_to_from_json(self, tbl, tmp_path, filename, compression):
        path = str(tmp_path / filename)
        tbl.to_json(path)

        result_tbl = Table.from_json(path)
        assert_matching_tables(tbl, result_tbl)

    @pytest.mark.parametrize("compression", [None, "gzip"], ids=["uncompressed", "compressed"])
    def test_to_from_temp_json(self, tbl, compression):
        path = tbl.to_json(temp_file_compression=compression) if compression else tbl.to_json()
        result_tbl = Table.from_json(path)
        assert_matching_tables(tbl, result_tbl)

    @pytest.mark.parametrize(
        ("filename", "compression"),
        [
            ("test.json", None),
            ("test.json.gz", "gzip"),
        ],
        ids=["uncompressed", "compressed"],
    )
    def test_to_from_json_line_delimited(self, tbl, tmp_path, filename, compression):
        path = str(tmp_path / filename)
        tbl.to_json(path, line_delimited=True)

        result_tbl = Table.from_json(path, line_delimited=True)
        assert_matching_tables(tbl, result_tbl)

    def test_to_html(self, tbl, tmp_path: Path):
        html_file = str(tmp_path / "test.html")

        # Test writing file
        tbl.to_html(html_file)

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

    def test_to_temp_html(self, tbl):
        # Test write to object
        path = Path(tbl.to_html())

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

    def test_to_petl(self, tbl):
        # Is a petl table
        assert isinstance(tbl.to_petl(), petl.io.json.DictsView)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_to_civis(self):
        # TODO: Not really sure the best way to do this at the moment.
        pass


class TestColumnOperations:
    """Tests for column manipulation operations"""

    @pytest.mark.parametrize(
        ("column", "expected"),
        [
            ("b", True),
            ("a", False),
        ],
        ids=["empty_column", "populated_column"],
    )
    def test_empty_column(self, column, expected):
        # Test that returns True on an empty column and False on a populated one.
        tbl = Table([["a", "b"], ["1", None], ["2", None]])
        assert tbl.empty_column(column) == expected

    def test_columns(self, tbl):
        # Test that columns are listed correctly
        assert tbl.columns == ["first", "last"]

    def test_add_column(self, tbl):
        # Test that a new column is added correctly
        tbl.add_column("middle", index=1)
        assert tbl.columns[1] == "middle"

    def test_column_add_dupe(self, tbl):
        # Test that we can't add an existing column name
        column = "first"
        with pytest.raises(ValueError, match=f"Column {column} already exists"):
            tbl.add_column(column)

    def test_add_column_if_exists(self, tbl):
        tbl.add_column("first", if_exists="replace")
        assert tbl.columns == ["first", "last"]

    def test_remove_column(self, tbl):
        # Test that column is removed correctly
        tbl.remove_column("first")
        assert tbl.data[0] != "first"

    def test_rename_column(self, tbl):
        # Test that you can rename a column
        tbl.rename_column("first", "f")
        assert tbl.columns[0] == "f"

    def test_column_rename_dupe(self, tbl):
        # Test that we can't rename to a column that already exists
        with pytest.raises(ValueError, match="Column first already exists"):
            tbl.rename_column("last", "first")

    @pytest.mark.parametrize(
        ("column_map", "expected_columns"),
        [
            ({"first": "firstname", "last": "lastname"}, ["firstname", "lastname"]),
            ({"first": "firstname"}, ["firstname", "last"]),
            ({}, ["first", "last"]),
        ],
        ids=["rename_all", "rename_partial", "rename_none"],
    )
    def test_rename_columns(self, tbl, column_map, expected_columns):
        # Test renaming columns with different scenarios
        tbl.rename_columns(column_map)
        assert tbl.columns == expected_columns

    def test_rename_columns_nonexistent(self, tbl):
        # Test renaming a column that doesn't exist
        column_map = {"nonexistent": "newname"}
        with pytest.raises(
            KeyError, match=f"Column name {next(iter(column_map.keys()))} does not exist"
        ):
            tbl.rename_columns(column_map)

    def test_rename_columns_duplicate(self, tbl):
        # Test renaming to a column name that already exists
        column_map = {"first": "last"}
        with pytest.raises(
            ValueError,
            match=f"Column name {column_map[next(iter(column_map.keys()))]} already exists",
        ):
            tbl.rename_columns(column_map)

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (0, [0, 0, 0, 0, 0]),
            (lambda x: x["b"] * 2, [4, 10, 16, 22, 28]),
        ],
        ids=["fixed_value", "calculated_value"],
    )
    def test_fill_column(self, sample_data, value, expected):
        # Test that the column is filled
        tbl = Table(sample_data["lst"])
        tbl.fill_column("c", value)
        assert list(tbl.table["c"]) == expected

    @pytest.mark.parametrize(
        ("column_name", "fill_value", "expected"),
        [
            ("b", "string-value", ["string-value", 5, 8, "string-value", 14]),
            ("c", 0, [3, 0, 9, 0, 15]),
            ("c", lambda r: r["a"] + r["b"], [3, 9, 9, None, 15]),
        ],
        ids=["string", "integer", "callable"],
    )
    def test_fillna_column(self, column_name: str, fill_value: Any, expected: list[Any]):
        # Test that None values in the column are filled

        lst = [
            {"a": 1, "b": None, "c": 3},
            {"a": 4, "b": 5, "c": None},
            {"a": 7, "b": 8, "c": 9},
            {"a": 10, "b": None, "c": None},
            {"a": 13, "b": 14, "c": 15},
        ]

        tbl = Table(lst)
        tbl.fillna_column(column_name=column_name, fill_value=fill_value)
        assert list(tbl.table[column_name]) == expected

    def test_move_column(self, tbl):
        # Test moving a column from end to front
        tbl.move_column("last", 0)
        assert tbl.columns[0] == "last"

    def test_convert_column(self, tbl):
        # Test that column updates
        tbl.convert_column("first", "upper")
        assert tbl[0] == {"first": "BOB", "last": "Smith"}

    @pytest.mark.parametrize(
        ("data", "expected_cols"),
        [
            ([], []),
            (
                [
                    {"col1": 1, "col2": "a"},
                    {"col1": "one", "col2": None},
                    {"col1": [1, 2], "col2": 3.0},
                ],
                ["col1", "col2"],
            ),
            ([{"col1": "hello", "col2": "world"}], ["col1", "col2"]),
        ],
    )
    def test_convert_columns_to_str(self, data: list[str | dict | int], expected_cols: list[str]):
        """Test that all columns are string"""
        tbl = Table(data)
        result = tbl.convert_columns_to_str()
        assert isinstance(result, Table)

        if tbl.num_rows > 0:
            cols_stats = tbl.get_columns_type_stats()
            for col in cols_stats:
                assert col["type"] == ["str"], f"Column {col['name']} was not converted to str"
        else:
            assert tbl.num_rows == 0

    def test_convert_table(self, tbl):
        # Test that the table updates
        tbl.convert_table("upper")
        assert tbl[0] == {"first": "BOB", "last": "SMITH"}

    @pytest.mark.parametrize(
        ("target_column", "source_columns", "test_data", "expected_data"),
        [
            (
                "last",
                ["last", "lastname"],
                [
                    {"first": "Bob", "last": "Smith", "lastname": None},
                    {"first": "Jane", "last": "", "lastname": "Doe"},
                    {"first": "Mary", "last": "Simpson", "lastname": "Peters"},
                ],
                [
                    {"first": "Bob", "last": "Smith"},
                    {"first": "Jane", "last": "Doe"},
                    {"first": "Mary", "last": "Simpson"},
                ],
            ),
            (
                "new_last",
                ["last", "lastname"],
                [
                    {"first": "Bob", "last": "Smith", "lastname": None},
                    {"first": "Jane", "last": "", "lastname": "Doe"},
                    {"first": "Mary", "last": "Simpson", "lastname": "Peters"},
                ],
                [
                    {"first": "Bob", "new_last": "Smith"},
                    {"first": "Jane", "new_last": "Doe"},
                    {"first": "Mary", "new_last": "Simpson"},
                ],
            ),
        ],
        ids=["coalesce_to_existing", "coalesce_to_new"],
    )
    def test_coalesce_columns(self, target_column, source_columns, test_data, expected_data):
        tbl = Table(test_data)
        tbl.coalesce_columns(target_column, source_columns)
        expected = Table(expected_data)
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

    @pytest.mark.parametrize(
        ("expand_original", "expected_columns", "expected_rows", "expected_uids"),
        [
            (False, ["uid", "id", "nested", "value"], 11, 11),
            (True, ["uid", "id", "extra", "nested", "nested_value"], 12, 12),
        ],
        ids=["standalone", "expanded"],
    )
    def test_unpack_nested_columns_as_rows(
        self, expand_original, expected_columns, expected_rows, expected_uids
    ):
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

        result = test_table.unpack_nested_columns_as_rows("nested", expand_original=expand_original)

        # Check that the columns are as expected
        assert result.columns == expected_columns

        # Check that the row count is as expected
        assert result.num_rows == expected_rows

        # Check that the uids are unique, indicating that each row is unique
        assert len({row["uid"] for row in result}) == expected_uids

    def test_cut(self, tbl):
        # Test that the cut works correctly
        cut_tbl = tbl.cut("first")
        assert cut_tbl.columns == ["first"]

    @pytest.mark.parametrize(
        ("column", "expected_width"),
        [
            ("a", 9),
            ("b", 5),
            ("c", 33),
        ],
        ids=["text", "non_string", "with_emojis"],
    )
    def test_get_column_max_with(self, column, expected_width):
        tbl = Table(
            [
                ["a", "b", "c"],
                ["wide_text", False, "slightly longer text"],
                ["text", 2, "byte_text🏽‍⚕️✊🏽🤩"],
            ]
        )
        assert tbl.get_column_max_width(column) == expected_width

    def test_column_data(self, sample_data):
        # Test that that the data in the column is returned as a list

        # Test a valid column
        tbl = Table(sample_data["lst"])
        lst = [1, 4, 7, 10, 13]
        assert tbl.column_data("a") == lst

        # Test an invalid column
        with pytest.raises(ValueError, match="Column name not found."):
            tbl.column_data("d")


class TestRowOperations:
    """Tests for row manipulation operations"""

    @pytest.mark.parametrize(
        ("selector", "expected"),
        [
            ("{foo} == 'a' and {baz} > 88.1", {"foo": "a", "bar": 2, "baz": 88.2}),
            (lambda row: row.foo == "a" and row.baz > 88.1, {"foo": "a", "bar": 2, "baz": 88.2}),
        ],
        ids=["string_selector", "lambda_selector"],
    )
    def test_row_select(self, selector, expected):
        tbl = Table([["foo", "bar", "baz"], ["c", 4, 9.3], ["a", 2, 88.2], ["b", 1, 23.3]])
        expected_tbl = Table([expected])

        select_tbl = tbl.select_rows(selector)
        assert select_tbl.data[0] == expected_tbl.data[0]

    @pytest.mark.parametrize(
        ("columns", "test_data", "expected_rows"),
        [
            ("b", [{"a": 1, "b": 2}, {"a": 1, "b": None}], 1),
            (["b", "c"], [{"a": 1, "b": 2, "c": 3}, {"a": 1, "b": None, "c": 3}], 1),
        ],
        ids=["single_column", "multiple_columns"],
    )
    def test_remove_null_rows(self, columns, test_data, expected_rows):
        null_table = Table(test_data)
        assert null_table.remove_null_rows(columns).num_rows == expected_rows

    @pytest.mark.parametrize(
        ("test_data", "retain_original", "expected_columns"),
        [
            ([{"id": 1, "tag": [1, 2, 3, 4]}], False, ["id"]),
            ([{"id": 1, "tag": [1, 2, 3, 4]}], True, ["id", "tag"]),
            ([{"id": 1, "tag": [1, 2, 3, 4]}, {"id": 2, "tag": None}], False, ["id"]),
            ([{"id": 1, "tag": [1, 2, 3, 4]}, {"id": 2, "tag": None}], True, ["id", "tag"]),
        ],
        ids=["basic", "retain_original", "with_na", "with_na_retain"],
    )
    def test_long_table(self, test_data, retain_original, expected_columns):
        tbl = Table(test_data)
        result = tbl.long_table(["id"], "tag", retain_original=retain_original)
        assert result.num_rows == 4
        assert tbl.columns == expected_columns

    def test_rows(self, tbl):
        # Test that there is only one row in the table
        assert tbl.num_rows == 1

    @pytest.mark.parametrize(
        ("test_data", "expected"),
        [
            ([{"first": "Bob", "last": "Smith"}], "Bob"),
            ([[1], [], [3]], None),
        ],
        ids=["with_data", "empty_first"],
    )
    def test_first(self, test_data, expected):
        tbl = Table(test_data)
        assert tbl.first == expected

    @pytest.mark.parametrize(
        ("index", "expected"),
        [
            ("a", [1, 4, 7, 10, 13]),
            (1, {"a": 4, "b": 5, "c": 6}),
        ],
        ids=["column_access", "row_access"],
    )
    def test_get_item(self, sample_data, index, expected):
        tbl = Table(sample_data["lst"])
        assert tbl[index] == expected

    def test_row_data(self, sample_data):
        # Test a valid column
        tbl = Table(sample_data["lst"])
        row = {"a": 4, "b": 5, "c": 6}
        assert tbl.row_data(1) == row

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

    @pytest.mark.parametrize(
        ("test_data", "keys", "presorted", "expected_data"),
        [
            # One column, no keys
            (
                [["a"], [1], [2], [2], [3]],
                None,
                True,
                [["a"], [1], [2], [3]],
            ),
            # Multiple columns, no keys
            (
                [["a", "b"], [1, 2], [1, 2], [1, 3], [2, 3]],
                None,
                True,
                [["a", "b"], [1, 2], [1, 3], [2, 3]],
            ),
            # Multiple columns, one key
            (
                [["a", "b"], [1, 3], [1, 2], [1, 2], [2, 3]],
                ["a"],
                True,
                [["a", "b"], [1, 3], [2, 3]],
            ),
            # Multiple columns, one key, not presorted
            (
                [["a", "b"], [2, 3], [1, 3], [1, 2], [1, 2]],
                ["a"],
                False,
                [["a", "b"], [1, 3], [2, 3]],
            ),
            # Multiple columns, two keys, not presorted
            (
                [["a", "b"], [2, 3], [1, 3], [1, 2], [1, 2]],
                ["a", "b"],
                False,
                [["a", "b"], [1, 2], [1, 3], [2, 3]],
            ),
            # Multiple columns, multiple keys
            (
                [["a", "b", "c"], [1, 2, 3], [1, 2, 3], [1, 2, 4], [1, 3, 2], [2, 3, 4]],
                ["a", "b"],
                True,
                [["a", "b", "c"], [1, 2, 3], [1, 3, 2], [2, 3, 4]],
            ),
        ],
        ids=[
            "one_col_no_keys",
            "multi_col_no_keys",
            "multi_col_one_key",
            "multi_col_one_key_unsorted",
            "multi_col_two_keys_unsorted",
            "multi_col_multi_keys",
        ],
    )
    def test_deduplicate(self, test_data, keys, presorted, expected_data):
        tbl = Table(test_data)
        tbl_expected = Table(expected_data)
        tbl.deduplicate(keys=keys, presorted=presorted)
        assert_matching_tables(tbl_expected, tbl)

    @pytest.mark.parametrize(
        ("method", "count", "expected_data"),
        [
            ("head", 2, [["a", "b"], [1, 2], [3, 4]]),
            ("tail", 2, [["a", "b"], [7, 8], [9, 10]]),
        ],
        ids=["head", "tail"],
    )
    def test_head_tail(self, method, count, expected_data):
        tbl = Table([["a", "b"], [1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])
        tbl_expected = Table(expected_data)
        getattr(tbl, method)(count)
        assert_matching_tables(tbl_expected, tbl)


class TestTableTransformations:
    """Tests for table-level transformations and combinations"""

    def test_stack(self, tbl):
        tbl1 = tbl.select_rows(lambda x: x)
        tbl2 = Table([{"first": "Mary", "last": "Nichols"}])
        tbl1.stack(tbl2)

        expected_tbl = Table(petl.stack(tbl.table, tbl2.table))
        assert_matching_tables(expected_tbl, tbl1)

        tbl1 = tbl.select_rows(lambda x: x)
        tbl2 = Table([{"first": "Mary", "last": "Nichols"}])
        # Different column names shouldn't matter for stack()
        tbl3 = Table([{"f": "Lucy", "l": "Peterson"}])
        tbl1.stack(tbl2, tbl3)

        expected_tbl = Table(petl.stack(tbl.table, tbl2.table, tbl3.table))
        assert_matching_tables(expected_tbl, tbl1)

    def test_concat(self, tbl):
        tbl1 = tbl.select_rows(lambda x: x)
        tbl2 = Table([{"first": "Mary", "last": "Nichols"}])
        tbl1.concat(tbl2)

        expected_tbl = Table(petl.cat(tbl.table, tbl2.table))
        assert_matching_tables(expected_tbl, tbl1)

        tbl1 = tbl.select_rows(lambda x: x)
        tbl2 = Table([{"first": "Mary", "last": "Nichols"}])
        tbl3 = Table([{"first": "Lucy", "last": "Peterson"}])
        tbl1.concat(tbl2, tbl3)

        expected_tbl = Table(petl.cat(tbl.table, tbl2.table, tbl3.table))
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

    def test_to_dicts(self, sample_data, tbl):
        assert sample_data["lst"] == Table(sample_data["lst"]).to_dicts()
        assert sample_data["lst_dicts"] == tbl.to_dicts()

    @pytest.mark.parametrize("exact_match", [True, False], ids=["exact", "fuzzy"])
    def test_map_columns(self, exact_match):
        if exact_match:
            input_tbl = Table([["fn", "ln", "MID"], ["J", "B", "H"]])
            expected_tbl = Table([["first_name", "last_name", "MID"], ["J", "B", "H"]])
        else:
            input_tbl = Table([["fn", "ln", "Mi_"], ["J", "B", "H"]])
            expected_tbl = Table([["first_name", "last_name", "middle_name"], ["J", "B", "H"]])

        column_map = {
            "first_name": ["fn", "first"],
            "last_name": ["last", "ln"],
            "middle_name": ["mi"],
        }

        input_tbl.map_columns(column_map, exact_match=exact_match)
        assert_matching_tables(input_tbl, expected_tbl)

    def test_map_and_coalesce_columns(self):
        input_tbl = Table([["fn", "ln", "mi"], ["J", "B", "H"]])
        expected_tbl = Table([["first_name", "last_name", "middle_name"], ["J", "B", "H"]])

        column_map = {
            "first_name": ["fn", "first"],
            "last_name": ["last", "ln"],
            "middle_name": ["mi"],
        }

        input_tbl.map_and_coalesce_columns(column_map=column_map)
        assert_matching_tables(input_tbl, expected_tbl)

    @pytest.mark.parametrize(
        ("sort_column", "reverse", "expected_first"),
        [
            (None, False, {"a": 1, "b": 3}),
            ("b", False, {"a": 3, "b": 1}),
            (None, True, {"a": 3, "b": 1}),
        ],
        ids=["basic_sort", "column_sort", "reverse_sort"],
    )
    def test_sort(self, sort_column, reverse, expected_first):
        unsorted_tbl = Table([["a", "b"], [3, 1], [2, 2], [1, 3]])
        if sort_column:
            sorted_tbl = unsorted_tbl.sort(sort_column)
        else:
            sorted_tbl = unsorted_tbl.sort(reverse=reverse)
        assert sorted_tbl[0] == expected_first

    @pytest.mark.parametrize(
        ("new_header", "expected_first"),
        [
            (["oneone", "twotwo"], {"oneone": 1, "twotwo": 2}),
            (["one"], {"one": 1}),
        ],
        ids=["rename_columns", "change_column_count"],
    )
    def test_set_header(self, new_header, expected_first):
        tbl = Table([["one", "two"], [1, 2], [3, 4]])
        new_tbl = tbl.set_header(new_header)
        assert new_tbl[0] == expected_first

    def test_bool(self):
        empty = Table()
        not_empty = Table([{"one": 1, "two": 2}])

        assert not empty
        assert not_empty

    def test_use_petl(self):
        # confirm that this method doesn't exist for parsons.Table
        with pytest.raises(
            AttributeError, match="type object 'Table' has no attribute 'skipcomments'"
        ):
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
