import time
from types import SimpleNamespace

import gspread
import pytest

from parsons import GoogleSheets, Table
from test.conftest import assert_matching_tables


@pytest.fixture
def sheets():
    """Provide a live GoogleSheets connector seeded with test spreadsheets.

    Yields a namespace bundling the connector along with the ids and tables
    created during setup. The spreadsheet is deleted on teardown.
    """
    google_sheets = GoogleSheets()

    spreadsheet_id = google_sheets.create_spreadsheet("parsons_test_01")
    test_table = Table(
        [
            {"first": "Bob", "last": "Smith"},
            {"first": "Sue", "last": "Doe"},
        ]
    )
    google_sheets.overwrite_sheet(spreadsheet_id, test_table)

    second_sheet_title = "2nd"
    google_sheets.add_sheet(spreadsheet_id, second_sheet_title)
    second_test_table = Table(
        [
            {"city": "San Francisco", "state": "SF"},
            {"city": "Chicago", "state": "IL"},
        ]
    )
    google_sheets.overwrite_sheet(spreadsheet_id, second_test_table, 1)
    time.sleep(10)

    yield SimpleNamespace(
        google_sheets=google_sheets,
        spreadsheet_id=spreadsheet_id,
        test_table=test_table,
        second_sheet_title=second_sheet_title,
        second_test_table=second_test_table,
    )

    google_sheets.delete_spreadsheet(spreadsheet_id)


@pytest.mark.live
def test_read_worksheet(sheets):
    table = sheets.google_sheets.get_worksheet(sheets.spreadsheet_id)
    assert table.num_rows == 2
    time.sleep(10)


@pytest.mark.live
def test_read_nonexistent_worksheet(sheets):
    bogus_title = "abc123"
    with pytest.raises(gspread.exceptions.APIError):
        sheets.google_sheets.read_sheet(bogus_title)


@pytest.mark.live
def test_create_spreadsheet(sheets):
    # Created as part of the sheets fixture
    assert sheets.spreadsheet_id is not None


@pytest.mark.live
def test_add_sheet(sheets):
    # Sheet added as part of the sheets fixture
    # Also tests get_sheet_index_with_title
    idx = sheets.google_sheets.get_worksheet_index(sheets.spreadsheet_id, sheets.second_sheet_title)
    assert idx == 1


@pytest.mark.live
def test_get_sheet_index_with_bogus_title(sheets):
    bogus_title = "abc123"
    with pytest.raises(ValueError, match=f"Couldn't find sheet with title {bogus_title}"):
        sheets.google_sheets.get_worksheet_index(
            sheets.spreadsheet_id,
            bogus_title,
        )


@pytest.mark.live
def test_read_worksheet_with_title(sheets):
    table = sheets.google_sheets.get_worksheet(sheets.spreadsheet_id, sheets.second_sheet_title)
    assert sheets.second_test_table.columns == table.columns


@pytest.mark.live
def test_append_to_spreadsheet(sheets):
    append_table = Table(
        [
            {"first": "Jim", "last": "Mitchell"},
            {"first": "Lucy", "last": "Simpson"},
        ]
    )
    sheets.google_sheets.append_to_sheet(sheets.spreadsheet_id, append_table)
    result_table = sheets.google_sheets.read_sheet(sheets.spreadsheet_id)

    assert append_table.columns == result_table.columns
    # We should now have rows from both tables
    assert sheets.test_table.num_rows + append_table.num_rows == result_table.num_rows

    # First check that we didn't muck with the original data
    for i in range(sheets.test_table.num_rows):
        assert list(sheets.test_table.data[i]) == result_table.data[i]
    orig_row_count = sheets.test_table.num_rows

    # Then check that we appended the data properly
    for i in range(append_table.num_rows):
        assert list(append_table.data[i]) == result_table.data[orig_row_count + i]

    # Test that we can append to an empty sheet
    sheets.google_sheets.add_sheet(sheets.spreadsheet_id, "Sheet3")
    sheets.google_sheets.append_to_sheet(sheets.spreadsheet_id, append_table)


@pytest.mark.live
def test_append_user_entered_to_spreadsheet(sheets):
    # Testing whether we can insert formulas with user_entered_value

    sheets.google_sheets.add_sheet(sheets.spreadsheet_id, "Sheet3")

    append_table = Table(
        [
            {"col1": 3, "col2": 9, "col3": "=A2*B2"},
            {"col1": "Buda", "col2": "Pest", "col3": "=A3&LOWER(B3)"},
        ]
    )
    sheets.google_sheets.append_to_sheet(
        sheets.spreadsheet_id, append_table, 2, user_entered_value=True
    )
    result_table = sheets.google_sheets.read_sheet(sheets.spreadsheet_id, 2)

    # Get the values from col3 which has fomulas
    formula_vals = [row["col3"] for row in result_table]

    # Test that the value is what's expected from each formula
    assert formula_vals[0] == "27"
    assert formula_vals[1] == "Budapest"
    time.sleep(10)


@pytest.mark.live
def test_paste_data_in_sheet(sheets):
    # Testing if we can paste data to a spreadsheet
    # TODO: there's probably a smarter way to test this code
    sheets.google_sheets.add_sheet(sheets.spreadsheet_id, "PasteDataSheet")

    paste_table1 = Table(
        [
            {"col1": 1, "col2": 2},
            {"col1": 5, "col2": 6},
        ]
    )
    paste_table2 = Table(
        [
            {"col3": 3, "col4": 4},
            {"col3": 7, "col4": 8},
        ]
    )
    paste_table3 = Table(
        [
            {"col1": 9, "col2": 10},
            {"col1": 13, "col2": 14},
        ]
    )
    paste_table4 = Table(
        [
            {"col3": 11, "col4": 12},
            {"col3": 15, "col4": 16},
        ]
    )

    # When we read the spreadsheet, it assumes data is all strings
    expected_table = Table(
        [
            {"col1": "1", "col2": "2", "col3": "3", "col4": "4"},
            {"col1": "5", "col2": "6", "col3": "7", "col4": "8"},
            {"col1": "9", "col2": "10", "col3": "11", "col4": "12"},
            {"col1": "13", "col2": "14", "col3": "15", "col4": "16"},
        ]
    )

    sheets.google_sheets.paste_data_in_sheet(
        sheets.spreadsheet_id,
        paste_table1,
        worksheet="PasteDataSheet",
        header=True,
        startrow=0,
        startcol=0,
    )
    sheets.google_sheets.paste_data_in_sheet(
        sheets.spreadsheet_id,
        paste_table2,
        worksheet="PasteDataSheet",
        header=True,
        startrow=0,
        startcol=2,
    )
    sheets.google_sheets.paste_data_in_sheet(
        sheets.spreadsheet_id,
        paste_table3,
        worksheet="PasteDataSheet",
        header=False,
        startrow=3,
        startcol=0,
    )
    sheets.google_sheets.paste_data_in_sheet(
        sheets.spreadsheet_id,
        paste_table4,
        worksheet="PasteDataSheet",
        header=False,
        startrow=3,
        startcol=2,
    )

    result_table = sheets.google_sheets.get_worksheet(sheets.spreadsheet_id, "PasteDataSheet")
    assert result_table.to_dicts() == expected_table.to_dicts()


@pytest.mark.live
def test_overwrite_spreadsheet(sheets):
    new_table = Table(
        [
            {"city": "San Francisco", "state": "CA"},
            {"city": "Miami", "state": "FL"},
            {"city": "San Antonio", "state": "TX"},
        ]
    )
    sheets.google_sheets.overwrite_sheet(sheets.spreadsheet_id, new_table)
    result_table = sheets.google_sheets.read_sheet(sheets.spreadsheet_id)

    assert_matching_tables(new_table, result_table)
    time.sleep(10)


@pytest.mark.live
def test_share_spreadsheet(sheets):
    # Test that sharing of spreadsheet works as intended.

    sheets.google_sheets.share_spreadsheet(
        sheets.spreadsheet_id, "bob@bob.com", role="reader", notify=True
    )
    permissions = sheets.google_sheets.get_spreadsheet_permissions(sheets.spreadsheet_id)
    assert "bob@bob.com" in permissions["emailAddress"]
