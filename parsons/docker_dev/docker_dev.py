import logging
from parsons import Table

##########

logger = logging.getLogger(__name__)


class Dev(object):
    """
    Dev class for Parsons / Docker demo
    """

    def __init__(self, tbl: Table):
        logger.debug("Setting up Dev instance...")
        self.table = tbl

    def make_all_columns_uppercase(self):
        upper_columns = [x.upper() for x in self.table.columns]
        return self.table.set_header(upper_columns)

    def make_all_columns_reversed(self):
        def reverse_string(x):
            return x

        reversed_columns = [reverse_string(x) for x in self.table.columns]
        return self.table.set_header(reversed_columns)

    def run(self):
        # NOTE - Toggle between these return statements
        return self.table
        # return self.make_all_columns_uppercase()
        # return self.make_all_columns_reversed()
