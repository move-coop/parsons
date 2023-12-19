import re

__all__ = ["redact_credentials", "get_sql_from_file"]


def redact_credentials(sql):
    """
    Redact any credentials explicitly represented in SQL (e.g. COPY statement)
    """

    pattern = "credentials\s+'(.+\n?)+[^(\\)]'"  # noqa: W605
    sql_censored = re.sub(pattern, "CREDENTIALS REDACTED", sql, flags=re.IGNORECASE)

    return sql_censored


def get_sql_from_file(sql_file):
    """
    Description:
        This function allows you to grab SQL defined in a separate file.
    `Args`:
        sql_file: str
            The relevant file path
    `Returns:`
        The SQL from the file
    """
    with open(sql_file, "r") as f:
        return f.read()
