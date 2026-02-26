"""Logging classes for use with Parsons dbt utility."""

import datetime
import logging
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Literal

from dbt.artifacts.schemas.results import NodeStatus
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown

from parsons import Table
from parsons.databases.database_connector import DatabaseConnector
from parsons.utilities.dbt.models import EnhancedNodeResult, Manifest

logger = logging.getLogger(__name__)


def human_readable_duration(seconds: int | float) -> str:
    time_struct = time.gmtime(seconds)

    time_str = ""

    if time_struct.tm_yday - 1:
        time_str += f"{time_struct.tm_yday - 1} days, "
    if time_struct.tm_hour:
        time_str += f"{time_struct.tm_hour} hours, "
    if time_struct.tm_min:
        time_str += f"{time_struct.tm_min} minutes, "
    if time_struct.tm_sec:
        time_str += f"{time_struct.tm_sec} seconds"

    return time_str


class dbtLogger(ABC):
    """Abstract base class for aggregating logs from dbt commands."""

    commands: list[Manifest]

    @abstractmethod
    def format_command_result(self, manifest: Manifest) -> str:
        pass

    @abstractmethod
    def format_result(self) -> str:
        pass

    @abstractmethod
    def send(self, manifests: list[Manifest]) -> None:
        """The send method is called to execute logging.

        manifests are passed to this method directly (rather
        than on initialization) so that the logger class can be
        initialized before the dbt commands have been run. This is
        mostly necessary for loggers that need to be initialized with
        credentials or options before being provided to the
        run_dbt_commands method.
        """
        self.commands = manifests
        log_text = self.format_result()  # noqa
        ...


class dbtLoggerMarkdown(dbtLogger):
    """Formats dbt results into a structured Markdown summary."""

    # Centralized mapping for status UI elements
    STATUS_MAP = {
        str(NodeStatus.Error): {"icon": "🔴", "text": "failed"},
        str(NodeStatus.Fail): {"icon": "🔴", "text": "failed"},
        str(NodeStatus.Warn): {"icon": "🟠", "text": "succeeded with warnings"},
        str(NodeStatus.Skipped): {"icon": "🔵", "text": "skipped"},
        str(NodeStatus.Success): {"icon": "🟢", "text": "succeeded"},
    }

    def _get_status_assets(
        self, manifest: Manifest | list[Manifest] | None = None
    ) -> dict[str, str]:
        """Helper to determine the emoji and text based on manifest status."""
        priority = [NodeStatus.Error, NodeStatus.Fail, NodeStatus.Warn, NodeStatus.Skipped]

        if isinstance(manifest, Manifest):
            key = manifest.overall_status if manifest else NodeStatus.Success
        elif isinstance(manifest, list) and all(isinstance(m, Manifest) for m in manifest):
            statuses = {m.overall_status for m in manifest}
            key = next((p for p in priority if p in statuses), NodeStatus.Success)
        else:
            raise TypeError(manifest)

        return self.STATUS_MAP.get(key, self.STATUS_MAP[str(NodeStatus.Success)])

    def format_command_result(self, manifest: Manifest) -> str:
        assets = self._get_status_assets(manifest)
        time_str = human_readable_duration(manifest.elapsed_time)

        log_message = f"{assets['icon']} Invoke dbt with `dbt {manifest.command}` ({manifest.overall_status} in {time_str})"

        log_summary_str = (
            ", ".join([f"{node}: {count}" for node, count in manifest.summary.items()])
            or "No models ran."
        )
        log_message += f"\n*Summary*: `{log_summary_str}`"
        log_message += f"\n*GB Processed*: {manifest.total_gb_processed:.2f}"
        log_message += f"\n*Slot hours*: {manifest.total_slot_hours:.2f}"

        # Error/Warning Blocks
        for label, nodes in [
            ("Error", [*manifest.errors, *manifest.fails]),
            ("Warn", manifest.warnings),
        ]:
            if nodes:
                msgs = "\n\n".join(
                    [f"{i.node.name}: {EnhancedNodeResult.log_message(i) or ''}" for i in nodes]
                )
                log_message += f"\n{label} messages:\n```\n{msgs}\n```"

        if manifest.skips:
            skips = {i.node.name for i in manifest.skips}
            log_message += f"\nSkipped:\n```\n{', '.join(skips)}\n```"

        return log_message

    def format_result(self) -> str:
        """
        Aggregates results from multiple dbt commands into a single
        report, determining an overall 'worst-case' status for the header.
        """
        assets = self._get_status_assets(self.commands)
        now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M")

        total_duration = sum([command.elapsed_time for command in self.commands])
        duration_str = human_readable_duration(total_duration)

        header = (
            f"{assets['icon']} *dbt run {assets['text']} - {now}*\n*Duration:* {duration_str}\n\n"
        )
        body = "\n".join([self.format_command_result(cmd) for cmd in self.commands])

        return header + body


class dbtLoggerStdout(dbtLoggerMarkdown):
    def send(self, manifests: list[Manifest]) -> None:
        self.commands = manifests
        log_text = self.format_result()

        md = Markdown(log_text)
        console = Console()
        console.print(md)


class dbtLoggerPython(dbtLoggerMarkdown):
    def send(self, manifests: list[Manifest]) -> None:
        self.commands = manifests
        log_text = self.format_result()

        if "RichHandler" not in [handler.__class__.__name__ for handler in logger.handlers]:
            logger.addHandler(RichHandler(level=logging.INFO))

        logger.info(log_text)


class dbtLoggerSlack(dbtLoggerMarkdown):
    def __init__(
        self,
        slack_webhook: str,
        slack_channel: str | None = None,
    ) -> None:
        self.slack_webhook = slack_webhook
        self.slack_channel = slack_channel

    def send(self, manifests: list[Manifest]) -> None:
        self.commands = manifests
        log_text = self.format_result()

        # Importing here to avoid needing to make slack-sdk a dependency for all dbt users
        from parsons.notifications.slack import Slack

        Slack.message(channel=self.slack_channel, text=log_text, webhook=self.slack_webhook)


class dbtLoggerDatabase(dbtLogger, ABC):
    """Log dbt artifacts by loading to a database.

    This class is an abstract base class for logging dbt artifacts to
    a database.
    """

    def __init__(
        self,
        database_connector: DatabaseConnector,
        destination_table_runs: str,
        destination_table_nodes: str,
        extra_run_table_fields: dict,
        **copy_kwargs,
    ) -> None:
        """Initialize the logger.

        Args:
            database_connector: A DatabaseConnector object.
            destination_table_runs: The name of the table to log run information.
            destination_table_nodes: The name of the table to log node information.
            extra_run_table_fields: A dictionary of additional fields to include in the run table.
            `**copy_kwargs`: Additional keyword arguments to pass to the `copy` method.

        """
        self.db_connector = database_connector
        self.destination_table_runs = destination_table_runs
        self.destination_table_nodes = destination_table_nodes
        self.extra_run_table_fields = extra_run_table_fields
        self.copy_kwargs = copy_kwargs

    def format_command_result(self, manifest: Manifest) -> tuple[Table, Table]:
        """Loads all artifact results into a Parsons Table."""
        dbt_run_id = str(uuid.uuid4())
        run_metadata = {
            key: getattr(manifest, key) for key in ("command", "generated_at", "elapsed_time")
        }
        run_metadata.update(**self.extra_run_table_fields)
        run_metadata["run_id"] = dbt_run_id
        run_tbl = Table([run_metadata])

        node_rows = []
        for result in manifest.results:
            node_row = {"dbt_run_id": dbt_run_id}
            node_row.update(
                {
                    key: value
                    for key, value in result.__dict__.items()
                    if key in ("execution_time", "message")
                }
            )
            node_row["status"] = str(result.status)
            node_info: dict[Literal["database", "schema", "name", "path", "node"], Any] = {
                key: value
                for key, value in result.node.__dict__.items()
                if key in ("database", "schema", "name", "path")
            }
            node_info["node"] = result.node.unique_id
            node_row.update(node_info)

            adapter_response_data = {
                key: value
                for key, value in result.adapter_response.items()
                if key in ("bytes_processed", "bytes_billed", "job_id", "slot_ms")
            }
            node_row.update(adapter_response_data)

            node_rows.append(node_row)

        nodes_tbl = Table(node_rows)
        return run_tbl, nodes_tbl

    def format_result(self) -> tuple[Table, Table]:
        """Returns a table for the dbt runs and a table for the node runs."""
        run_rows = []
        node_rows = []
        for command in self.commands:
            run_tbl, nodes_tbl = self.format_command_result(command)
            run_rows.extend(run_tbl.to_dicts())
            node_rows.extend(nodes_tbl.to_dicts())

        all_runs_tbl = Table(run_rows)
        all_nodes_tbl = Table(node_rows)
        return all_runs_tbl, all_nodes_tbl

    def send(self, manifests: list[Manifest]) -> None:
        self.commands = manifests
        runs_tbl, nodes_tbl = self.format_result()

        if len(runs_tbl):
            self.db_connector.copy(
                runs_tbl,
                self.destination_table_runs,
                if_exists="append",
                **self.copy_kwargs,
            )
        if len(nodes_tbl):
            self.db_connector.copy(
                nodes_tbl,
                self.destination_table_nodes,
                if_exists="append",
                **self.copy_kwargs,
            )
