from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class FakeDatabase:
    def __init__(self):
        self.table_map = {}
        self.copy_call_args = []

    def setup_table(self, table_name, data, failures=0):
        self.table_map[table_name] = {
            "failures": failures,
            "table": FakeTable(table_name, data),
        }
        return self.table_map[table_name]["table"]

    def table(self, table_name):
        if table_name not in self.table_map:
            self.setup_table(table_name, None)

        return self.table_map[table_name]["table"]

    def copy(self, data, table_name, **kwargs):
        logger.info("Copying %s rows", data.num_rows)
        if table_name not in self.table_map:
            self.setup_table(table_name, Table())

        if self.table_map[table_name]["table"].data is None:
            self.table_map[table_name]["table"].data = Table()

        if self.table_map[table_name]["failures"] > 0:
            self.table_map[table_name]["failures"] -= 1
            raise ValueError("Canned error")

        self.copy_call_args.append(
            {
                "data": data,
                "table_name": table_name,
                "kwargs": kwargs,
            }
        )

        tbl = self.table_map[table_name]["table"]

        tbl.data.concat(data)

    def get_table_object(self, table_name):

        pass

    def create_table(self, table_object, table_name):

        pass


class FakeTable:
    def __init__(self, table_name, data):
        self.table_name = table_name
        self.data = data

    def drop(self, cascade=False):
        self.data = None

    def truncate(self):
        self.data = Table()

    def distinct_primary_key(self, primary_key):
        if primary_key not in self.data.columns:
            return True

        pk_values = [val for val in self.data[primary_key]]
        pk_set = set(pk_values)
        return len(pk_set) == len(pk_values)

    @property
    def columns(self):
        return self.data.columns

    def max_primary_key(self, primary_key):
        if primary_key not in self.data.columns:
            return None

        return max(self.data[primary_key])

    @property
    def num_rows(self):
        return self.data.num_rows

    @property
    def exists(self):
        return self.data is not None

    def get_rows(self, offset=0, chunk_size=None, order_by=None):
        data = self.data.cut(*self.data.columns)

        if order_by:
            data.sort(order_by)

        return Table(data[offset : chunk_size + offset])

    def get_new_rows_count(self, primary_key_col, start_value=None):
        data = self.data.select_rows(lambda row: row[primary_key_col] > start_value)
        return data.num_rows

    def get_new_rows(self, primary_key, cutoff_value, offset=0, chunk_size=None):
        data = self.data.select_rows(lambda row: row[primary_key] > cutoff_value)
        data.sort(primary_key)

        return Table(data[offset : chunk_size + offset])
