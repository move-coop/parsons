# Additional padding to add on to the maximum column width to account
# for the addition of future data sets.
VARCHAR_PAD = 0.25

COL_NAME_MAX_LEN = 64

# List of varchar lengths to use for columns -- this list needs to be in order from smallest to
# largest
VARCHAR_STEPS = [32, 64, 128, 256, 512, 1024, 4096, 8192, 16384]

# Max length of a Redshift VARCHAR column
VARCHAR_MAX = 65535

# The following values are the minimum and maximum values for MySQL int
# types. https://dev.mysql.com/doc/refman/8.0/en/integer-types.html
SMALLINT_VALUES = [-32768, 32767]
MEDIUMINT_VALUES = [-8388608, 8388607]
INT_VALUES = [-2147483648, 2147483647]
