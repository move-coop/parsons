from parsons.databases.database.constants import (
    SMALLINT, MEDIUMINT, INT, BIGINT, FLOAT, VARCHAR)

from parsons.databases.database.database import DatabaseCreateStatement

import pytest


@pytest.fixture
def dcs():
    return DatabaseCreateStatement()


@pytest.mark.parametrize(
    ("int1", "int2", "higher"),
    ((SMALLINT, SMALLINT, SMALLINT),
     (SMALLINT, MEDIUMINT, MEDIUMINT),
     (SMALLINT, INT, INT),
     (SMALLINT, BIGINT, BIGINT),
     (MEDIUMINT, SMALLINT, MEDIUMINT),
     (MEDIUMINT, MEDIUMINT, MEDIUMINT),
     (MEDIUMINT, INT, INT),
     (MEDIUMINT, BIGINT, BIGINT),
     (INT, SMALLINT, INT),
     (INT, MEDIUMINT, INT),
     (INT, INT, INT),
     (INT, BIGINT, BIGINT),
     (BIGINT, SMALLINT, BIGINT),
     (BIGINT, MEDIUMINT, BIGINT),
     (BIGINT, INT, BIGINT),
     (BIGINT, BIGINT, BIGINT),
     (None, BIGINT, BIGINT),
     (INT, None, INT),
     ))
def test_get_bigger_int(dcs, int1, int2, higher):
    assert dcs.get_bigger_int(int1, int2) == higher


@pytest.mark.parametrize(
    ("val", "is_valid"),
    ((10, True),
     (1_0, True),
     (+10, True),
     (+1_0, True),
     (1.2, True),
     (1.0_0, True),
     (1., True),
     (1_0., True),
     (+1.2, True),
     (+1., True),
     (+1.0_0, True),
     ("10", True),
     ("1_0", False),
     ("+10", True),
     ("+1_0", False),
     ("1.2", True),
     ("1.0_0", False),
     ("1.", True),
     ("1_0.", False),
     ("+1.2", True),
     ("+1.", True),
     ("+1.0_0", False),
     (True, False),
     ("True", False),
     ("a string", False),
     ({}, False),
     ([], False),
     ([], False),
     (None, False),
     ))
def test_is_valid_sql_num(dcs, val, is_valid):
    assert dcs.is_valid_sql_num(val) == is_valid


@pytest.mark.parametrize(
    ("val", "cmp_type", "detected_type"),
    ((1, None, SMALLINT),
     (1, "", SMALLINT),
     (1, MEDIUMINT, MEDIUMINT),
     (32769, None, MEDIUMINT),
     (32769, BIGINT, BIGINT),
     (2147483648, None, BIGINT),
     (2147483648, FLOAT, FLOAT),
     (5.001, None, FLOAT),
     (5.001, "", FLOAT),
     ("word", "", VARCHAR),
     ("word", INT, VARCHAR),
     ("1_2", BIGINT, VARCHAR),
     ("01", FLOAT, VARCHAR),
     ("00001", None, VARCHAR),
     ("word", None, VARCHAR),
     ("1_2", None, VARCHAR),
     ("01", None, VARCHAR),
     ))
def test_detect_data_type(dcs, val, cmp_type, detected_type):
    assert dcs.detect_data_type(val, cmp_type) == detected_type


@pytest.mark.parametrize(
    ("col", "renamed"),
    (("a", "a"),
     ("A", "a"),
     ("", "_"),
     ("SELECT", "select_"),
     ("two words", "two_words"),
     ("   trailing space   ", "trailing_space"),
     ("1234567890", "x_1234567890"),
     ("0word", "x_0word"),

     # create a really long column name
     # len("asdfghjkla" * 13) == 130
     # len("asdfghjkla" * 10) == 100
     ("asdfghjkla" * 13, "asdfghjkla" * 10),
     ))
def test_default_format_column(dcs, col, renamed):
    assert dcs.format_column(col) == renamed


@pytest.mark.parametrize(
    ("cols", "cols_formatted"),
    ((["a", "A", "b", "   b   ", "col name", "col_name"],
      ["a", "a_1", "b", "b_3", "col_name", "col_name_5"]),
     ))
def test_default_format_columns(dcs, cols, cols_formatted):
    assert dcs.format_columns(cols) == cols_formatted
