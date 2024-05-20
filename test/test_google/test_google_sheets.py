import unittest
import gspread
import os

from parsons import GoogleSheets, Table
from test.utils import assert_matching_tables


@unittest.skipIf(not os.environ.get("LIVE_TEST"), "Skipping because not running live test")
class TestGoogleSheets(unittest.TestCase):
    def setUp(self):

        self.google_sheets = GoogleSheets()

        self.spreadsheet_id = self.google_sheets.create_spreadsheet("parsons_test_01")
        self.test_table = Table(
            [
                {"first": "Bob", "last": "Smith"},
                {"first": "Sue", "last": "Doe"},
            ]
        )
        self.google_sheets.overwrite_sheet(self.spreadsheet_id, self.test_table)

        self.second_sheet_title = "2nd"
        self.google_sheets.add_sheet(self.spreadsheet_id, self.second_sheet_title)
        self.second_test_table = Table(
            [
                {"city": "San Francisco", "state": "SF"},
                {"city": "Chicago", "state": "IL"},
            ]
        )
        self.google_sheets.overwrite_sheet(self.spreadsheet_id, self.second_test_table, 1)

    def tearDown(self):
        # self.google_sheets.delete_spreadsheet(self.spreadsheet_id)
        pass

    def test_read_worksheet(self):
        # This is the spreadsheet called "Legislators 2017 (Test sheet for Parsons)"
        table = self.google_sheets.get_worksheet("1Y_pZxz-8JZ9QBdq1pXuIk2js_VXeymOUoZhUp1JVEg8")
        self.assertEqual(541, table.num_rows)

    def test_read_sheet(self):
        # Deprecated in Parsons v0.14

        # This is the spreadsheet called "Legislators 2017 (Test sheet for Parsons)"
        table = self.google_sheets.read_sheet("1Y_pZxz-8JZ9QBdq1pXuIk2js_VXeymOUoZhUp1JVEg8")
        self.assertEqual(541, table.num_rows)

    def test_read_nonexistent_worksheet(self):
        self.assertRaises(gspread.exceptions.APIError, self.google_sheets.read_sheet, "abc123")

    def test_create_spreadsheet(self):
        # Created as part of setUp
        self.assertIsNotNone(self.spreadsheet_id)

    def test_add_sheet(self):
        # Sheet added as part of setUp
        # Also tests get_sheet_index_with_title
        idx = self.google_sheets.get_worksheet_index(self.spreadsheet_id, self.second_sheet_title)
        self.assertEqual(1, idx)

    def test_get_sheet_index_with_bogus_title(self):
        self.assertRaises(
            ValueError,
            self.google_sheets.get_worksheet_index,
            self.spreadsheet_id,
            "abc123",
        )

    def test_read_worksheet_with_title(self):
        table = self.google_sheets.get_worksheet(self.spreadsheet_id, self.second_sheet_title)
        self.assertEqual(self.second_test_table.columns, table.columns)

    def test_append_to_spreadsheet(self):
        # BROKEN TEST!
        append_table = Table(
            [
                {"first": "Jim", "last": "Mitchell"},
                {"first": "Lucy", "last": "Simpson"},
            ]
        )
        self.google_sheets.append_to_sheet(self.spreadsheet_id, append_table)
        result_table = self.google_sheets.read_sheet(self.spreadsheet_id)

        self.assertEqual(append_table.columns, result_table.columns)
        # We should now have rows from both tables
        self.assertEqual(self.test_table.num_rows + append_table.num_rows, result_table.num_rows)

        # First check that we didn't muck with the original data
        for i in range(self.test_table.num_rows):
            self.assertEqual(self.test_table.data[i], result_table.data[i])
        orig_row_count = self.test_table.num_rows

        # Then check that we appended the data properly
        for i in range(append_table.num_rows):
            self.assertEqual(append_table.data[i], result_table.data[orig_row_count + i])

        # Test that we can append to an empty sheet
        self.google_sheets.add_sheet(self.spreadsheet_id, "Sheet3")
        self.google_sheets.append_to_sheet(self.spreadsheet_id, append_table)

    def test_append_user_entered_to_spreadsheet(self):
        # Testing whether we can insert formulas with user_entered_value

        self.google_sheets.add_sheet(self.spreadsheet_id, "Sheet3")

        append_table = Table(
            [
                {"col1": 3, "col2": 9, "col3": "=A2*B2"},
                {"col1": "Buda", "col2": "Pest", "col3": "=A3&LOWER(B3)"},
            ]
        )
        self.google_sheets.append_to_sheet(
            self.spreadsheet_id, append_table, 2, user_entered_value=True
        )
        result_table = self.google_sheets.read_sheet(self.spreadsheet_id, 2)

        # Get the values from col3 which has fomulas
        formula_vals = [row["col3"] for row in result_table]

        # Test that the value is what's expected from each formula
        self.assertEqual(formula_vals[0], "27")
        self.assertEqual(formula_vals[1], "Budapest")

    def test_paste_data_in_sheet(self):
        # Testing if we can paste data to a spreadsheet
        # TODO: there's probably a smarter way to test this code
        self.google_sheets.add_sheet(self.spreadsheet_id, "PasteDataSheet")

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

        self.google_sheets.paste_data_in_sheet(
            self.spreadsheet_id,
            paste_table1,
            worksheet="PasteDataSheet",
            header=True,
            startrow=0,
            startcol=0,
        )
        self.google_sheets.paste_data_in_sheet(
            self.spreadsheet_id,
            paste_table2,
            worksheet="PasteDataSheet",
            header=True,
            startrow=0,
            startcol=2,
        )
        self.google_sheets.paste_data_in_sheet(
            self.spreadsheet_id,
            paste_table3,
            worksheet="PasteDataSheet",
            header=False,
            startrow=3,
            startcol=0,
        )
        self.google_sheets.paste_data_in_sheet(
            self.spreadsheet_id,
            paste_table4,
            worksheet="PasteDataSheet",
            header=False,
            startrow=3,
            startcol=2,
        )

        result_table = self.google_sheets.get_worksheet(self.spreadsheet_id, "PasteDataSheet")
        self.assertEqual(result_table.to_dicts(), expected_table.to_dicts())

    def test_overwrite_spreadsheet(self):
        new_table = Table(
            [
                {"city": "San Francisco", "state": "CA"},
                {"city": "Miami", "state": "FL"},
                {"city": "San Antonio", "state": "TX"},
            ]
        )
        self.google_sheets.overwrite_sheet(self.spreadsheet_id, new_table)
        result_table = self.google_sheets.read_sheet(self.spreadsheet_id)

        assert_matching_tables(new_table, result_table)

    def test_share_spreadsheet(self):
        # Test that sharing of spreadsheet works as intended.

        self.google_sheets.share_spreadsheet(
            self.spreadsheet_id, "bob@bob.com", role="reader", notify=True
        )
        permissions = self.google_sheets.get_spreadsheet_permissions(self.spreadsheet_id)
        self.assertIn("bob@bob.com", permissions["emailAddress"])
