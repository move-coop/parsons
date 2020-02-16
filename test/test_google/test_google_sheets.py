import unittest
import gspread
import warnings
import os

from parsons.google.google_sheets import GoogleSheets
from parsons.etl.table import Table


@unittest.skipIf(not os.environ.get('LIVE_TEST'), 'Skipping because not running live test')
class TestGoogleSheets(unittest.TestCase):

    def setUp(self):

        self.google_sheets = GoogleSheets()

        self.spreadsheet_id = self.google_sheets.create_spreadsheet('Parsons Test')
        self.test_table = Table([
            {'first': 'Bob', 'last': 'Smith'},
            {'first': 'Sue', 'last': 'Doe'},
        ])
        self.google_sheets.overwrite_sheet(self.spreadsheet_id, self.test_table)

        self.second_sheet_title = "2nd sheet"
        self.google_sheets.add_sheet(self.spreadsheet_id, self.second_sheet_title)
        self.second_test_table = Table([
            {'city': 'San Francisco', 'state': 'SF'},
            {'city': 'Chicago', 'state': 'IL'},
        ])
        self.google_sheets.overwrite_sheet(self.spreadsheet_id, self.second_test_table, 1)

    def tearDown(self):
        self.google_sheets.delete_spreadsheet(self.spreadsheet_id)

    def test_read_sheet(self):
        # This is the spreadsheet called "Legislators 2017 (Test sheet for Parsons)"
        table = self.google_sheets.read_sheet('1Y_pZxz-8JZ9QBdq1pXuIk2js_VXeymOUoZhUp1JVEg8')
        self.assertEqual(541, table.num_rows)

    def test_read_nonexistent_sheet(self):
        self.assertRaises(gspread.exceptions.APIError, self.google_sheets.read_sheet, 'abc123')

    def test_create_spreadsheet(self):
        # Created as part of setUp
        self.assertIsNotNone(self.spreadsheet_id)

    def test_add_sheet(self):
        # Sheet added as part of setUp
        # Also tests get_sheet_index_with_title
        idx = self.google_sheets.get_sheet_index_with_title(
            self.spreadsheet_id, self.second_sheet_title
            )
        self.assertEqual(1, idx)

    def test_get_sheet_index_with_bogus_title(self):
        self.assertRaises(
            ValueError,
            self.google_sheets.get_sheet_index_with_title, self.spreadsheet_id, 'abc123'
            )

    def test_read_sheet_with_title(self):
        table = self.google_sheets.read_sheet_with_title(self.spreadsheet_id, self.second_sheet_title)
        self.assertEqual(self.second_test_table.columns, table.columns)

    def test_append_to_spreadsheet(self):
        append_table = Table([
            {'first': 'Jim', 'last': 'Mitchell'},
            {'first': 'Lucy', 'last': 'Simpson'},
        ])
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
            self.assertEqual(append_table.data[i], result_table.data[orig_row_count+i])

    def test_append_user_entered_to_spreadsheet(self):
        # Testing whether we can insert formulas with user_entered_value
        append_table = Table([
            {'col1': 3, 'col2': 9, 'col3': '=A2*B2'},
            {'col1': 'Buda', 'col2': 'Pest', 'col3': '=A3&LOWER(B3)'},
        ])
        self.google_sheets.append_to_sheet(self.spreadsheet_id, append_table,
            user_entered_value=True)
        result_table = self.google_sheets.read_sheet(self.spreadsheet_id)

        # Get the values from col3 which has fomulas
        formula_vals = [row['col3'] for row in result_table]

        # Test that the value is what's expected from each formula
        self.assertEqual(formula_vals[0], 27)
        self.assertEqual(formula_vals[1], 'Budapest')

    def test_overwrite_spreadsheet(self):
        new_table = Table([
            {'city': 'San Francisco', 'state': 'CA'},
            {'city': 'Miami', 'state': 'FL'},
            {'city': 'San Antonio', 'state': 'TX'},
        ])
        self.google_sheets.overwrite_sheet(self.spreadsheet_id, new_table)
        result_table = self.google_sheets.read_sheet(self.spreadsheet_id)

        self.assertEqual(new_table.columns, result_table.columns)
        self.assertEqual(new_table.num_rows, result_table.num_rows)
        for i in range(new_table.num_rows):
            self.assertEqual(new_table.data[i], result_table.data[i])

