import re

__all__ = ["redact_credentials"]


def redact_credentials(sql):
    """
    Redact any credentials explicitly represented in SQL (e.g. COPY statement)
    """

    pattern = "credentials\s+'(.+\n?)+[^(\\)]'"  # noqa: W605
    sql_censored = re.sub(pattern, "CREDENTIALS REDACTED", sql, flags=re.IGNORECASE)

    return sql_censored
