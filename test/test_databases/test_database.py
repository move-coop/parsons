from parsons.databases.database.constants import (
    SMALLINT,
    MEDIUMINT,
    INT,
    BIGINT,
    BOOL,
    VARCHAR,
)

from parsons.databases.database.database import DatabaseCreateStatement

import pytest


@pytest.fixture
def dcs():
    db = DatabaseCreateStatement()
    return db


@pytest.mark.parametrize(
    ("int1", "int2", "higher"),
    (
        (SMALLINT, SMALLINT, SMALLINT),
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
    ),
)
def test_get_bigger_int(dcs, int1, int2, higher):
    assert dcs.get_bigger_int(int1, int2) == higher


@pytest.mark.parametrize(
    ("val", "is_valid"),
    (
        (10, True),
        (1_0, True),
        (+10, True),
        (+1_0, True),
        (1.2, True),
        (1.0_0, True),
        (1.0, True),
        (1_0.0, True),
        (+1.2, True),
        (+1.0, True),
        (+1.0_0, True),
        (0, True),
        (0.0, True),
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
        ("0", True),
        ("0.0", True),
        (True, False),
        ("True", False),
        ("a string", False),
        ({}, False),
        ([], False),
        ([], False),
        (None, False),
    ),
)
def test_is_valid_sql_num(dcs, val, is_valid):
    assert dcs.is_valid_sql_num(val) == is_valid


@pytest.mark.parametrize(
    ("val", "cmp_type", "detected_type"),
    (
        (2, None, SMALLINT),
        (2, "", SMALLINT),
        (1, MEDIUMINT, MEDIUMINT),
        (2, BOOL, SMALLINT),
        (True, None, BOOL),
        (0, None, SMALLINT),
        (1, None, SMALLINT),
        (1, BOOL, SMALLINT),
        ("F", None, VARCHAR),
        ("FALSE", None, VARCHAR),
        ("Yes", None, VARCHAR),
    ),
)
def test_detect_data_type_bools(dcs, val, cmp_type, detected_type):
    assert dcs.detect_data_type(val, cmp_type) == detected_type


@pytest.mark.parametrize(
    ("col", "renamed"),
    (
        ("a", "a"),
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
    ),
)
def test_default_format_column(dcs, col, renamed):
    assert dcs.format_column(col) == renamed


@pytest.mark.parametrize(
    ("cols", "cols_formatted"),
    (
        (
            ["a", "A", "b", "   b   ", "col name", "col_name"],
            ["a", "a_1", "b", "b_3", "col_name", "col_name_5"],
        ),
    ),
)
def test_default_format_columns(dcs, cols, cols_formatted):
    assert dcs.format_columns(cols) == cols_formatted
