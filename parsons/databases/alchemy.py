import logging

from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class Alchemy:
    def generate_engine(self) -> Engine:
        """Generate a SQL Alchemy engine."""
        alchemy_url = self.generate_alchemy_url()
        return create_engine(alchemy_url, echo=False, convert_unicode=True)

    def generate_alchemy_url(self) -> str:
        """Generate a SQL Alchemy :class:`~sqlalchemy.engine.Engine`."""
        if self.dialect == "redshift" or self.dialect == "postgres":
            connection_schema = "postgresql+psycopg2"
        elif self.dialect == "mysql":
            connection_schema = "mysql+mysqlconnector"

        params = [
            (self.username, self.username),
            (self.password, f":{self.password}"),
            (self.host, f"@{self.host}"),
            (self.port, f":{self.port}"),
            (self.db, f"/{self.db}"),
        ]

        url = f"{connection_schema}://"

        for i in params:
            if i[0]:
                url += i[1]

        return url

    def get_table_object(self, table_name) -> Table:
        """Get a SQL Alchemy :class:`sqlalchemy.schema.Table`."""
        schema, table_name = self.split_table_name(table_name)
        db_meta = MetaData(bind=self.generate_engine(), schema=schema)
        return Table(table_name, db_meta, autoload=True)

    def create_table(self, table_object, table_name) -> None:
        """Create a table based on :class:`sqlalchemy.schema.Table` data."""
        schema, table_name = self.split_table_name(table_name)

        if schema:
            table_object.schema = schema
        if table_name:
            table_object.table_name = table_name

        table_object.metadata.create_all(self.generate_engine())

    @staticmethod
    def split_table_name(full_table_name: str) -> tuple[str | None, str | None]:
        """Parse the schema and table name."""
        if "." not in full_table_name:
            return "public", full_table_name

        try:
            schema, table = full_table_name.split(".")
            return schema, table

        except ValueError as e:
            if "too many values to unpack" in str(e):
                raise ValueError(f"Invalid database table {full_table_name}") from e

        return None, None
