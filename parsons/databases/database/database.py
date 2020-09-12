from parsons.databases.database.constants import (
    INT_TYPES, INT, INT_MIN, INT_MAX, SMALLINT, SMALLINT_MIN, SMALLINT_MAX,
    MEDIUMINT, MEDIUMINT_MIN, MEDIUMINT_MAX, BIGINT, FLOAT, VARCHAR)

import ast


class DatabaseCreateStatement():

    def __init__(self):
        self.INT_TYPES = INT_TYPES
        self.SMALLINT = SMALLINT
        self.SMALLINT_MIN = SMALLINT_MIN
        self.SMALLINT_MAX = SMALLINT_MAX
        self.MEDIUMINT = MEDIUMINT
        self.MEDIUMINT_MIN = MEDIUMINT_MIN
        self.MEDIUMINT_MAX = MEDIUMINT_MAX
        self.INT = INT
        self.INT_MIN = INT_MIN
        self.INT_MAX = INT_MAX
        self.BIGINT = BIGINT
        self.FLOAT = FLOAT
        self.VARCHAR = VARCHAR

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
            if (float(val) or int(val)) and '_' not in val and val[0] != '0':
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
            return cmp_type

        # Attempt to evaluate value as a literal (e.g. '1' => 1, ) If the value
        # is just a string, is None, or is empty, it will raise an error. These
        # should be considered varchars.
        # E.g.
        # "" => SyntaxError
        # "anystring" => ValueError
        try:
            val_lit = ast.literal_eval(str(value))
        except (SyntaxError, ValueError):
            return self.VARCHAR

        # Exit early if it's None
        # is_valid_sql_num(None) == False
        # instead of defaulting to varchar (which is the next test)
        # return the compare type
        if val_lit is None:
            return cmp_type

        # Make sure that it is a valid integer
        # Python accepts 100_000 as a valid form of 100000,
        # however a sql engine may throw an error
        if not self.is_valid_sql_num(value):
            return self.VARCHAR

        type_lit = type(val_lit)

        # If a float, stop here
        # float is highest after varchar
        if type_lit == float or cmp_type == self.FLOAT:
            return self.FLOAT

        # The value is very likely an int
        # let's get its size
        if type_lit == int and cmp_type in (self.INT_TYPES + [None]):

            # Use smallest possible int type above TINYINT
            if (self.SMALLINT_MIN < val_lit < self.SMALLINT_MAX):
                return self.get_bigger_int(self.SMALLINT, cmp_type)
            elif (self.MEDIUMINT_MIN < val_lit < self.MEDIUMINT_MAX):
                return self.get_bigger_int(self.MEDIUMINT, cmp_type)
            elif (self.INT_MIN < val_lit < self.INT_MAX):
                return self.get_bigger_int(self.INT, cmp_type)
            else:
                return self.BIGINT

        # Need to determine who makes it all the way down here
        return cmp_type
