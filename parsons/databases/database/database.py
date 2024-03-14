import parsons.databases.database.constants as consts
import logging

logger = logging.getLogger(__name__)


class DatabaseCreateStatement:
    def __init__(self):
        self.INT_TYPES = consts.INT_TYPES
        self.SMALLINT = consts.SMALLINT
        self.SMALLINT_MIN = consts.SMALLINT_MIN
        self.SMALLINT_MAX = consts.SMALLINT_MAX
        self.MEDIUMINT = consts.MEDIUMINT
        self.MEDIUMINT_MIN = consts.MEDIUMINT_MIN
        self.MEDIUMINT_MAX = consts.MEDIUMINT_MAX
        self.INT = consts.INT
        self.INT_MIN = consts.INT_MIN
        self.INT_MAX = consts.INT_MAX
        self.BIGINT = consts.BIGINT
        self.FLOAT = consts.FLOAT

        self.BOOL = consts.BOOL

        self.VARCHAR = consts.VARCHAR
        self.RESERVED_WORDS = consts.RESERVED_WORDS
        self.COL_NAME_MAX_LEN = consts.COL_NAME_MAX_LEN
        self.IS_CASE_SENSITIVE = consts.IS_CASE_SENSITIVE
        self.REPLACE_CHARS = consts.REPLACE_CHARS

    # This will allow child classes to modify how these columns are handled.
    def _rename_reserved_word(self, col, index=None):
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
        return f"{col}_"

    def _rename_duped(self, col, index):
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
        return f"{col}_{index}"

    def get_bigger_int(self, int1, int2):
        """Return the bigger of the two ints.

        `Args`:
            int1: str
                The string representation if an int type.
            int2: str
                The string representation if an int type.
        `Returns`:
            str
                A string representation of the higher of the two int types.
        """
        WEIGHTS = {
            self.SMALLINT: 100,
            self.MEDIUMINT: 200,
            self.INT: 300,
            self.BIGINT: 400,
        }

        return int1 if WEIGHTS.get(int1, -1) >= WEIGHTS.get(int2, -1) else int2

    def is_valid_sql_num(self, val):
        """Check whether val is a valid sql number.

        `Args`:
            val: any
                The values to check.
        `Returns`:
            bool
                Whether or not the value is a valid sql number.
        """
        # Python accepts numbers with single-underscore separators such as
        # 100_000 (evals to 100000)
        # SQL engines may not support this

        # If its python type is a number, then it's a number
        # 100_000 is stored at 100000 in memory so it's fine
        # not using `isinstance` b/c isinstance(bool. (int, float)) == True
        if type(val) in (int, float):
            return True

        # If it can be cast to a number and it doesn't contain underscores
        # then it's a valid sql number
        # Also check the first character is not zero
        try:
            if (float(val) or 1) and "_" not in val and (val in ("0", "0.0") or val[0] != "0"):
                return True
            else:
                return False

        # If it can't be cast to a number in python
        # then it's not a number in sql
        except (TypeError, ValueError):
            return False

    def detect_data_type(self, value, cmp_type=None):
        """Detect the higher of value's type cmp_type.

        1. check if it's a string
        2. check if it's a number
          a. check if it's a float
          b. check if it's an int

        `Args`:
            value: str
                The value to inspect.
            cmp_type: str
                The string representation of a type to compare with
                ``value``'s type.
        `Returns`:
            str
                The string representation of the higher of the two types.
        """
        # Stop if the compare type is already a varchar
        # varchar is the highest data type.
        if cmp_type == self.VARCHAR:
            result = cmp_type

        elif isinstance(value, bool):
            result = self.BOOL

        elif value is None:
            result = cmp_type

        # Make sure that it is a valid integer
        # Python accepts 100_000 as a valid form of 100000,
        # however a sql engine may throw an error
        elif not self.is_valid_sql_num(value):
            result = self.VARCHAR

        elif isinstance(value, float) or cmp_type == self.FLOAT:
            result = self.FLOAT

        # The value is very likely an int
        # let's get its size
        # If the compare types are empty and use the types of the current value
        elif isinstance(value, int) and cmp_type in (self.INT_TYPES + [None, "", self.BOOL]):
            # Use smallest possible int type above TINYINT
            if self.SMALLINT_MIN < value < self.SMALLINT_MAX:
                result = self.get_bigger_int(self.SMALLINT, cmp_type)
            elif self.MEDIUMINT_MIN < value < self.MEDIUMINT_MAX:
                result = self.get_bigger_int(self.MEDIUMINT, cmp_type)
            elif self.INT_MIN < value < self.INT_MAX:
                result = self.get_bigger_int(self.INT, cmp_type)
            else:
                result = self.BIGINT

        else:
            # Need to determine who makes it all the way down here
            logger.debug(f"Unexpected object type: {type(value)}")
            result = cmp_type

        return result

    def format_column(self, col, index="", replace_chars=None, col_prefix="_"):
        """Format the column to meet database contraints.

        Formats the columns as follows:
            1. Coverts to lowercase (if case insensitive)
            2. Strips leading and trailing whitespace
            3. Replaces invalid characters
            4. Renames if in reserved words
        `Args`:
            col: str
                The column to format.
            index: int
                (Optional) The index of the column. Used if the column is empty.
            replace_chars: dict
                A dictionary of invalid characters and their replacements. If
                ``None`` uses {" ": "_"}
            col_prefix: str
                The prefix to use when the column is empty or starts with an
                invalid character.
        `Returns`:
            str
                The formatted column.
        """
        replace_chars = replace_chars or self.REPLACE_CHARS

        if not self.IS_CASE_SENSITIVE:
            col = col.lower()

        col = col.strip()

        for char, rep_char in replace_chars.items():
            col = col.replace(char, rep_char)

        # The format for this column passes all other checks
        if col == "":
            return f"{col_prefix}{index}"

        if col.upper() in self.RESERVED_WORDS:
            col = self._rename_reserved_word(col, index)

        if col[0].isdigit():
            col = f"x_{col}"

        if len(col) > self.COL_NAME_MAX_LEN:
            col = col[: self.COL_NAME_MAX_LEN]

        return col

    def format_columns(self, cols, **kwargs):
        """Format the columns to meet database contraints.

        This method relies on ``format_column`` to handle most changes. It
        only handles duplicated columns. Options to ``format_column`` can be
        passed through kwargs.

        `Args`:
            cols: list
                The columns to format.
            kwargs: dicts
                Keyword arguments to pass to ``format_column``.
        `Returns`:
            list
                The formatted columns.
        """
        formatted_cols = []

        for idx, col in enumerate(cols):
            formatted_col = self.format_column(col, index=idx, **kwargs)

            if formatted_col in formatted_cols:
                formatted_col = self._rename_duped(formatted_col, idx)

            formatted_cols.append(formatted_col)

        return formatted_cols
