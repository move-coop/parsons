from typing import Optional, Any
from idrt.algorithm.database_adapter import DatabaseAdapter, EtlTable

from parsons import Table
from parsons.databases.database_connector import DatabaseConnector
from parsons.databases.redshift import Redshift


def has_method(obj: Any, method_name: str) -> bool:
    return callable(getattr(obj, method_name))


class ParsonsDBAdapter(DatabaseAdapter):
    """Provide access to use any Parsons database connector in the IDRT algorithm."""

    def __init__(self, db: DatabaseConnector):
        """Create the database adapter.

        Args:
            db (DatabaseConnector): The Parsons DatabaseConnector you wish to use.
                Must support the upsert method!
        """
        if not has_method(db, "upsert"):
            raise RuntimeError(
                f"DatabaseConnector instance {type(db)} does not support upsert"
            )
        self._db = db

    def _table_exists(self, tablename: str) -> bool:
        return self._db.table_exists(tablename)

    def _execute_query(self, query: str) -> Optional[EtlTable]:
        result = self._db.query(query)
        if result is None:
            return result
        return result.to_petl()

    def _upsert(self, tablename: str, data: EtlTable, primary_key: Any):
        if isinstance(self._db, Redshift):
            self._db.upsert(Table(data), tablename, primary_key, vacuum=False)
        else:
            # We checked in the constructor that _db supports the upsert operation.
            self._db.upsert(Table(data), tablename, primary_key)  # type: ignore

    def _bulk_upload(self, tablename: str, data: EtlTable):
        self._db.copy(Table(data), tablename, if_exists="drop")
