"""Logging classes for use with Parsons dbt utility."""

import datetime
import logging
import time
import uuid
from abc import ABC, abstractmethod
from typing import Optional

from dbt.contracts.graph.manifest import Manifest
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown

from parsons import Table
from parsons.databases.database_connector import DatabaseConnector
from parsons.utilities.dbt.models import EnhancedNodeResult

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
    def format_command_result(
        self,
        manifest: Manifest,
    ) -> str:
        log_message = ""

        # Header
        if manifest.errors:
            log_message += "\U0001f534"  # Red box
            status = "Error"
        elif manifest.warnings:
            log_message += "\U0001f7e0"  # Orange circle
            status = "Warning"
        else:
            log_message += "\U0001f7e2"  # Green circle
            status = "Success"

        time_str = human_readable_duration(manifest.elapsed_time)
        log_message += f"Invoke dbt with `dbt {manifest.command}` ({status} in {time_str})"

        log_summary_str = ", ".join(
            [f"{node}: {count}" for node, count in manifest.summary.items()]
        )
        if not log_summary_str:
            log_summary_str = "No models ran."
        log_message += "\n*Summary*: `{}`".format(log_summary_str)

        log_message += "\n*GB Processed*: {:.2f}".format(manifest.total_gb_processed)
        log_message += "\n*Slot hours*: {:.2f}".format(manifest.total_slot_hours)

        # Errors
        if manifest.errors or manifest.fails:
            log_message += "\nError messages:\n```{}```".format(
                "\n\n".join(
                    [
                        i.node.name + ": " + (EnhancedNodeResult.log_message(i) or "")
                        for i in [*manifest.errors, *manifest.fails]
                    ]
                )
            )

        # Warnings
        if manifest.warnings:
            log_message += "\nWarn messages:\n```{}```".format(
                "\n\n".join(
                    [
                        i.node.name + ": " + (EnhancedNodeResult.log_message(i) or "")
                        for i in manifest.warnings
                    ]
                )
            )

        # Skips
        if manifest.skips:
            skips = {i.node.name for i in manifest.skips}
            log_message += "\nSkipped:\n```{}```".format(", ".join(skips))

        return log_message

    def format_result(self) -> str:
        """Format result string from all commands."""
        full_log_message = ""

        # Header
        if any(command.errors for command in self.commands):
            status = "failed"
            full_log_message += "\U0001f534"
        else:
            status = "succeeded"
            full_log_message += "\U0001f7e2"

        now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M")
        full_log_message += f"*dbt run {status} - {now}*"

        total_duration = sum([command.elapsed_time for command in self.commands])
        duration_time_str = human_readable_duration(total_duration)
        full_log_message += f"\n*Duration:* {duration_time_str}\n\n"

        # Formatted results from each command
        log_messages = [self.format_command_result(command) for command in self.commands]
        full_log_message += "\n".join(log_messages)

        return full_log_message


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
        slack_channel: Optional[str] = None,
    ) -> None:
        self.slack_webhook = slack_webhook
        self.slack_channel = slack_channel

    def send(self, manifests: list[Manifest]) -> None:
        self.commands = manifests
        log_text = self.format_result()

        # Importing here to avoid needing to make slackclient a dependency for all dbt users
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
            **copy_kwargs: Additional keyword arguments to pass to the `copy` method.
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
            node_info = {
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
