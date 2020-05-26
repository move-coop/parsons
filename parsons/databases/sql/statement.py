from parsons.databases.sql.select import SelectStatementBuilder


def select(*args, **kwargs):
    return (SelectStatementBuilder()
            .select(*args, **kwargs))
