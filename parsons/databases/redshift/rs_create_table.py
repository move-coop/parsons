from parsons.databases.database.database import DatabaseCreateStatement
import parsons.databases.redshift.constants as consts

import petl
import logging

logger = logging.getLogger(__name__)


class RedshiftCreateTable(DatabaseCreateStatement):
    def __init__(self):
        super().__init__()

        self.COL_NAME_MAX_LEN = consts.COL_NAME_MAX_LEN
        self.REPLACE_CHARS = consts.REPLACE_CHARS

        # Currently smallints are coded as ints
        self.SMALLINT = self.INT
        # Redshift doesn't have a medium int
        self.MEDIUMINT = self.INT

        # Currently py floats are coded as Redshift decimals
        self.FLOAT = consts.FLOAT

        self.VARCHAR_MAX = consts.VARCHAR_MAX
        self.VARCHAR_STEPS = consts.VARCHAR_STEPS

    # the default behavior is f"{col}_"
    def _rename_reserved_word(self, col, index):
        """Return the renamed column.

        `Args`:
            col: str
                The column to rename.
            index: int
                (Optional) The index of the column.
        `Returns`:
            str
                The rename column.
        """
        return f"col_{index}"

    def create_statement(
        self,
        tbl,
        table_name,
        padding=None,
        distkey=None,
        sortkey=None,
        varchar_max=None,
        varchar_truncate=True,
        columntypes=None,
        strict_length=True,
    ):
        # Warn the user if they don't provide a DIST key or a SORT key
        self._log_key_warning(distkey=distkey, sortkey=sortkey, method="copy")

        # Generate a table create statement

        # Validate and rename column names if needed
        tbl.table = petl.setheader(tbl.table, self.column_name_validate(tbl.columns))

        if tbl.num_rows == 0:
            raise ValueError("Table is empty. Must have 1 or more rows.")

        mapping = self.generate_data_types(tbl)

        if padding:
            mapping["longest"] = self.vc_padding(mapping, padding)
        elif not strict_length:
            mapping["longest"] = self.vc_step(mapping)

        if varchar_max:
            mapping["longest"] = self.vc_max(mapping, varchar_max)

        if varchar_truncate:
            mapping["longest"] = self.vc_trunc(mapping)

        mapping["longest"] = self.vc_validate(mapping)

        # Add any provided column type overrides
        if columntypes:
            for i in range(len(mapping["headers"])):
                col = mapping["headers"][i]
                if columntypes.get(col):
                    mapping["type_list"][i] = columntypes[col]

        # Enclose in quotes
        mapping["headers"] = ['"{}"'.format(h) for h in mapping["headers"]]

        return self.create_sql(table_name, mapping, distkey=distkey, sortkey=sortkey)

    # This is for backwards compatability
    def data_type(self, val, current_type):
        return self.detect_data_type(val, current_type)

    # This is for backwards compatability
    def is_valid_integer(self, val):
        return self.is_valid_sql_num(val)

    def generate_data_types(self, table):
        # Generate column data types

        longest, type_list = [], []

        cont = petl.records(table.table)

        # Populate empty values for the columns
        for col in table.columns:
            longest.append(0)
            type_list.append("")

        for row in cont:
            for i in range(len(row)):
                # NA is the csv null value
                if type_list[i] == "varchar" or row[i] in ["NA", ""]:
                    pass
                else:
                    var_type = self.data_type(row[i], type_list[i])
                    type_list[i] = var_type

                # Calculate width
                if len(str(row[i]).encode("utf-8")) > longest[i]:
                    longest[i] = len(str(row[i]).encode("utf-8"))

        # In L138 'NA' and '' will be skipped
        # If the entire column is either one of those (or a mix of the two)
        # the type will be empty.
        # Fill with a default varchar
        type_list = [typ or "varchar" for typ in type_list]

        return {"longest": longest, "headers": table.columns, "type_list": type_list}

    def vc_padding(self, mapping, padding):
        # Pad the width of a varchar column

        return [int(c + (c * padding)) for c in mapping["longest"]]

    def vc_step(self, mapping):
        return [self.round_longest(c) for c in mapping["longest"]]

    def vc_max(self, mapping, columns):
        # Set the varchar width of a column to the maximum

        for c in columns:
            try:
                idx = mapping["headers"].index(c)
                mapping["longest"][idx] = self.VARCHAR_MAX

            except KeyError as error:
                logger.error("Could not find column name provided.")
                raise error

        return mapping["longest"]

    def vc_trunc(self, mapping):
        return [self.VARCHAR_MAX if c > self.VARCHAR_MAX else c for c in mapping["longest"]]

    def vc_validate(self, mapping):
        return [1 if c == 0 else c for c in mapping["longest"]]

    def create_sql(self, table_name, mapping, distkey=None, sortkey=None):
        # Generate the sql to create the table

        statement = "create table {} (".format(table_name)

        for i in range(len(mapping["headers"])):
            if mapping["type_list"][i] == "varchar":
                statement = (statement + "\n  {} varchar({}),").format(
                    str(mapping["headers"][i]).lower(), str(mapping["longest"][i])
                )
            else:
                statement = (statement + "\n  " + "{} {}" + ",").format(
                    str(mapping["headers"][i]).lower(), mapping["type_list"][i]
                )

        statement = statement[:-1] + ") "

        if distkey:
            statement += "\ndistkey({}) ".format(distkey)

        if sortkey and isinstance(sortkey, list):
            statement += "\ncompound sortkey("
            statement += ", ".join(sortkey)
            statement += ")"
        elif sortkey:
            statement += "\nsortkey({})".format(sortkey)

        statement += ";"

        return statement

    # This is for backwards compatability
    def column_name_validate(self, columns):
        return self.format_columns(columns, col_prefix="col_")

    @staticmethod
    def _log_key_warning(distkey=None, sortkey=None, method=""):
        # Log a warning message advising the user about DIST and SORT keys

        if distkey and sortkey:
            return

        keys = [
            (
                distkey,
                "DIST",
                "https://aws.amazon.com/about-aws/whats-new/2019/08/amazon-redshift-"
                "now-recommends-distribution-keys-for-improved-query-performance/",
            ),
            (
                sortkey,
                "SORT",
                "https://docs.amazonaws.cn/en_us/redshift/latest/dg/c_best-practices-"
                "sort-key.html",
            ),
        ]
        warning = "".join(
            [
                "You didn't provide a {} key to method `parsons.redshift.Redshift.{}`.\n"
                "You can learn about best practices here:\n{}.\n".format(keyname, method, keyinfo)
                for key, keyname, keyinfo in keys
                if not key
            ]
        )

        warning += "You may be able to further optimize your queries."

        logger.warning(warning)

    @staticmethod
    def round_longest(longest):
        # Find the value that will work best to fit our longest column value
        for step in consts.VARCHAR_STEPS:
            # Make sure we have padding
            if longest < step / 2:
                return step

        return consts.VARCHAR_MAX
