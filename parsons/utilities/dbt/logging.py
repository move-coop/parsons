"""Logging classes for use with Parsons dbt utility."""

import datetime
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown

from dbt.contracts.graph.manifest import Manifest

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
            log_message += "\U0001F534"  # Red box
            status = "Error"
        elif manifest.warnings:
            log_message += "\U0001F7E0"  # Orange circle
            status = "Warning"
        else:
            log_message += "\U0001F7E2"  # Green circle
            status = "Success"

        time_str = human_readable_duration(manifest.elapsed_time)
        log_message += f"Invoke dbt with `dbt {manifest.command}` ({status} in {time_str})"

        log_summary_str = ", ".join(
            [f"{node}: {count}" for node, count in manifest.summary.items()]
        )
        if not log_summary_str:
            log_summary_str = "No models ran."
        log_message += "\n*Summary*: `{}`".format(log_summary_str)

        # Errors
        if manifest.errors:
            log_message += "\nError messages:\n```{}```".format(
                "\n\n".join([i.node.name + ": " + i.message for i in manifest.errors])
            )

        # Warnings
        if manifest.warnings:
            log_message += "\nWarn messages:\n```{}```".format(
                "\n\n".join([i.node.name + ": " + i.message for i in manifest.warnings])
            )

        # Skips
        if manifest.skips:
            skips = set([i.node.name for i in manifest.skips])
            log_message += "\nSkipped:\n```{}```".format(", ".join(skips))

        return log_message

    def format_result(self) -> str:
        """Format result string from all commands."""
        full_log_message = ""

        # Header
        if any([command.errors for command in self.commands]):
            status = "failed"
            full_log_message += "\U0001F534"
        else:
            status = "succeeded"
            full_log_message += "\U0001F7E2"

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
