import ast
import petl
import logging

logger = logging.getLogger(__name__)

"""
To do:
	- Look at is valid integer
	- Add column name validate
"""

class MySQLCreateTable():

    def __init__(self):

        pass

    def data_type(self, val, current_type):
        # Determine the MySQL data type of a given value

        try:
            # Convert to string to reevaluate data type
            t = ast.literal_eval(str(val))
        except ValueError:
            return 'varchar'
        except SyntaxError:
            return 'varchar'

        if type(t) in [int, float]:
            if (type(t) in [int] and current_type not in ['float', 'varchar']):

                # Make sure that it is a valid integer
                if not self.is_valid_integer(val):
                    return 'varchar'

                # Use smallest possible int type above TINYINT
                if (-32768 < t < 32767) and current_type not in ['int', 'bigint', 'mediumint']:
                    return 'smallint'
                elif (-8388608 < t < 8388607) and current_type not in ['int', 'bigint']:
                	return 'mediumint'
                elif (-2147483648 < t < 2147483647) and current_type not in ['bigint']:
                    return 'int'
                else:
                    return 'bigint'
            if type(t) is float and current_type not in ['varchar']:
                return 'decimal'
        else:
            return 'varchar'

    def is_valid_integer(self, val):

        # Valid ints in python can contain an underscore, but Redshift can't. This
        # checks to see if there is an underscore in the value and turns it into
        # a varchar if so.
        try:
            if '_' in val:
                return False

        except TypeError:
            return True

        # If it has a leading zero, we should treat it as a varchar, since it is
        # probably there for a good reason (e.g. zipcode)
        if val.isdigit():
            if val[0] == '0':
                return False

        return True

    def evaluate_column(self, column_rows):
        # Generate column data types

        col_width = 0
        col_type = None

        # Iterate through each row in the column
        for row in column_rows:

            # Get the MySQL data type
            col_type = self.data_type(row, col_type)

            # Calculate width if a varchar
            if col_type == 'varchar':
                row_width = len(str(row.encode('utf-8')))

                # Evaluate width vs. current max width
                if row_width > col_width:
                    col_width = row_width

        return col_type, col_width

    def evaluate_table(self, tbl):

        table_map = []

        for col in tbl.columns:
            col_type, col_width = self.evaluate_column(tbl.column_data(col))
            col_map = {'name': col, 'type': col_type, 'width': col_width}
            table_map.append(col_map)

        return table_map

    def create_statement(self, table_name, table_map):

        # Generate the column syntax
        column_syntax = []
        for c in table_map:
            if c['type'] == 'varchar':
                column_syntax.append(f"{c['name']} {c['type']}({c['width']}) \n")
            else:
                column_syntax.append(f"{c['name']} {c['type']} \n")

        # Generate full statement
        return f"CREATE TABLE {table_name} ( \n {','.join(column_syntax)});"