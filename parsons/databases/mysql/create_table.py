from parsons.databases.database.database import DatabaseCreateStatement
import parsons.databases.mysql.constants as consts

import petl
import logging

logger = logging.getLogger(__name__)


class MySQLCreateTable(DatabaseCreateStatement):
    def __init__(self):
        super().__init__()

        self.VARCHAR_PAD = consts.VARCHAR_PAD
        self.COL_NAME_MAX_LEN = consts.COL_NAME_MAX_LEN
        self.RESERVED_WORDS = []
        self.VARCHAR_STEPS = consts.VARCHAR_STEPS
        self.VARCHAR_MAX = consts.VARCHAR_MAX
        self.SMALLINT_VALUES = consts.SMALLINT_VALUES
        self.MEDIUMINT_VALUES = consts.MEDIUMINT_VALUES
        self.INT_VALUES = consts.INT_VALUES

    # This is for backwards compatability
    def data_type(self, val, current_type):
        return self.detect_data_type(val, current_type)

    # This is for backwards compatability
    def is_valid_integer(self, val):
        return self.is_valid_sql_num(val)

    def evaluate_column(self, column_rows):
        # Generate MySQL data types and widths for a column.

        col_width = 0
        col_type = None

        # Iterate through each row in the column
        for row in column_rows:

            # Get the MySQL data type
            col_type = self.data_type(row, col_type)

            # Calculate width if a varchar
            if col_type == "varchar":
                row_width = len(str(row.encode("utf-8")))

                # Evaluate width vs. current max width
                if row_width > col_width:
                    col_width = row_width

        return col_type, col_width

    def evaluate_table(self, tbl):
        # Generate a dict of MySQL column types and widths for all columns
        # in a table.

        table_map = []

        for col in tbl.columns:
            col_type, col_width = self.evaluate_column(tbl.column_data(col))
            col_map = {"name": col, "type": col_type, "width": col_width}
            table_map.append(col_map)

        return table_map

    def create_statement(self, tbl, table_name, strict_length=True):
        # Generate create statement SQL for a given Parsons table.

        # Validate and rename column names if needed
        tbl.table = petl.setheader(tbl.table, self.columns_convert(tbl.columns))

        # Generate the table map
        table_map = self.evaluate_table(tbl)

        # Generate the column syntax
        column_syntax = []
        for c in table_map:
            if strict_length:
                col_width = int(c["width"] + (self.VARCHAR_PAD * c["width"]))
            else:
                col_width = self.round_longest(c["width"])

            if c["type"] == "varchar":
                column_syntax.append(f"{c['name']} {c['type']}({col_width}) \n")
            else:
                column_syntax.append(f"{c['name']} {c['type']} \n")

        # Generate full statement
        return f"CREATE TABLE {table_name} ( \n {','.join(column_syntax)});"

    # This is for backwards compatability
    def columns_convert(self, columns):
        return self.format_columns(columns, col_prefix="col_")

    @staticmethod
    def round_longest(longest):
        # Find the value that will work best to fit our longest column value
        for step in consts.VARCHAR_STEPS:
            # Make sure we have padding
            if longest < step / 2:
                return step

        return consts.VARCHAR_MAX
