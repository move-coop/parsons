import logging
import os

from parsons.databases.mysql import MySQL
from parsons.databases.postgres import Postgres
from parsons.databases.redshift import Redshift

logger = logging.getLogger(__name__)

DEFAULT_DIALECT_KEY = 'DIALECT'


def get_config_value(config, base_key, prefix=None):
    if prefix:
        key = f'{prefix}{base_key}'
    else:
        key = base_key
    return config.get(key)


def build_database_connector(prefix=None, dialect=None, config=os.environ, **kwargs):
    dialect_key = DEFAULT_DIALECT_KEY

    if prefix:
        dialect_key = f'{prefix}{dialect_key}'

    if not dialect:
        if dialect_key not in os.environ:
            raise KeyError(f'Could not find dialect in the environment in key "{dialect_key}"')

        dialect = os.environ[dialect_key]

    if not prefix:
        prefix = dialect.upper()

    if dialect.lower() == "redshift":
        return Redshift(
            username=get_config_value(config, 'USERNAME', prefix),
            password=get_config_value(config, 'PASSWORD', prefix),
            host=get_config_value(config, 'HOST', prefix),
            db=get_config_value(config, 'DB', prefix),
            port=get_config_value(config, 'PORT', prefix),
            **kwargs
        )

    if dialect.lower() == "postgres":
        return Postgres(
            username=get_config_value(config, 'USERNAME', prefix),
            password=get_config_value(config, 'PASSWORD', prefix),
            host=get_config_value(config, 'HOST', prefix),
            db=get_config_value(config, 'DB', prefix),
            port=get_config_value(config, 'PORT', prefix),
            **kwargs
        )

    if dialect.lower() == "mysql":
        return MySQL(
            username=get_config_value(config, 'USERNAME', prefix),
            password=get_config_value(config, 'PASSWORD', prefix),
            host=get_config_value(config, 'HOST', prefix),
            db=get_config_value(config, 'DB', prefix),
            port=get_config_value(config, 'PORT', prefix),
            **kwargs
        )

    raise ValueError(f'Unknown database dialect: {dialect}')
