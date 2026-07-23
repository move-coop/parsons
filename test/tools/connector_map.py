"""Map a connector name to its source module and test path.

Used by ``test/tools/parity.py`` to scope per-connector coverage and mutation
runs. The *connector name* is the suffix of its test directory
(``test/test_<name>``) and, for most connectors, the parsons extra name.

Most connectors resolve by the default rule ``parsons/<name>`` +
``test/test_<name>``. The exceptions — where a connector's source lives
somewhere other than ``parsons/<name>/`` — are listed in ``_OVERRIDES``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Connector:
    """A resolved connector: where its code lives and how to test it."""

    name: str
    source_path: str  # dir or file to mutate/cover, relative to repo root
    cov_module: str  # dotted module passed to `coverage --source` / `--cov`
    test_path: str  # pytest target, relative to repo root


# Connectors whose source is NOT parsons/<name>/. Keep this list in sync as
# connectors move; `validate()` will flag a mapping that no longer resolves.
_OVERRIDES: dict[str, tuple[str, str]] = {
    "s3": ("parsons/aws/s3.py", "parsons.aws.s3"),
    "smtp": ("parsons/notifications/smtp.py", "parsons.notifications.smtp"),
    "slack": ("parsons/notifications/slack.py", "parsons.notifications.slack"),
    "ssh": ("parsons/utilities/ssh_utilities.py", "parsons.utilities.ssh_utilities"),
    "facebook": ("parsons/facebook_ads", "parsons.facebook_ads"),
    "mysql": ("parsons/databases/mysql", "parsons.databases.mysql"),
    "postgres": ("parsons/databases/postgres", "parsons.databases.postgres"),
    "redshift": ("parsons/databases/redshift", "parsons.databases.redshift"),
    "dbt-duckdb": ("parsons/utilities/dbt", "parsons.utilities.dbt"),
    "dbt-redshift": ("parsons/utilities/dbt", "parsons.utilities.dbt"),
    "dbt-bigquery": ("parsons/utilities/dbt", "parsons.utilities.dbt"),
    "dbt-postgres": ("parsons/utilities/dbt", "parsons.utilities.dbt"),
    "dbt-snowflake": ("parsons/utilities/dbt", "parsons.utilities.dbt"),
    # These extras exercise broad, shared ETL modules; the scope is approximate
    # and coverage/mutation numbers will be noisier than a dedicated connector.
    "avro": ("parsons/etl/tofrom.py", "parsons.etl.tofrom"),
    "pandas": ("parsons/etl/tofrom.py", "parsons.etl.tofrom"),
}


def resolve(name: str) -> Connector:
    """Resolve a connector name to its source module and test path."""
    if name in _OVERRIDES:
        source_path, cov_module = _OVERRIDES[name]
    else:
        source_path = f"parsons/{name}"
        cov_module = f"parsons.{name}"
    return Connector(
        name=name,
        source_path=source_path,
        cov_module=cov_module,
        test_path=f"test/test_{name}",
    )


def validate(conn: Connector) -> list[str]:
    """Return a list of problems with a resolved connector (empty if it's fine)."""
    problems = []
    if not (REPO_ROOT / conn.source_path).exists():
        problems.append(
            f"source path not found: {conn.source_path} "
            f"(add an entry to _OVERRIDES in test/tools/connector_map.py)"
        )
    if not (REPO_ROOT / conn.test_path).exists():
        problems.append(f"test path not found: {conn.test_path}")
    return problems
