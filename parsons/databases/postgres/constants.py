COL_NAME_MAX_LEN = 120

DECIMAL = "decimal"

REPLACE_CHARS = {" ": ""}

# Max length of a Redshift VARCHAR column
VARCHAR_MAX = 65535

# List of varchar lengths to use for columns -- this list needs to be in order from smallest to
# largest
VARCHAR_STEPS = [32, 64, 128, 256, 512, 1024, 4096, 8192, 16384]
