"""Utility for running and logging output from dbt commands

Enable this utility by installing parsons with a dbt extra:
`pip install parsons[dbt-redshift]`
or `pip install parsons[dbt-postgres]`
or `pip install parsons[dbt-snowflake]`
or `pip install parsons[dbt-bigquery]`

To run dbt commands, you will need to have a dbt project directory
somewhere on the local filesystem.

If slack-related arguments or environment variables are not provided,
no log message will be sent to slack.

Example usage:
```
from parsons.utilities.dbt import dbtRunner

dbt_runner = dbtRunner(
    commands=['run', 'test'],
    dbt_project_directory='/home/ubuntu/code/dbt_project/',
    dbt_schema='dbt_dev'
)
dbt_runner.run()
```
"""

import datetime
import json
import logging
import os
import pathlib
import shutil
import subprocess
import time
from typing import List, Literal, Optional

from parsons.notifications.slack import Slack
from parsons.utilities import check_env

logger = logging.getLogger(__name__)


class dbtLogger:
    """Module for aggregating logs between dbt commands and sending to slack."""

    _command_times: dict[str, dict[Literal["start", "end"], float]] = {}

    def __init__(
        self,
        slack_channel: Optional[str] = None,
        slack_webhook: Optional[str] = None,
        slack_api_key: Optional[str] = None,
    ):
        self.start = time.time()
        self.log_messages = []
        self.error_messages = []
        self.warn_messages = []
        self.done_messages = []
        self.slack_channel = slack_channel
        self.slack_webhook = slack_webhook
        self.slack_api_key = slack_api_key

    def record_start(self, command: str) -> None:
        """Record start time for command"""
        self._command_times[command] = {"start": time.time()}

    def record_end(self, command: str) -> None:
        """Record end time for command"""
        self._command_times[command]["end"] = time.time()

    def seconds_to_time_string(self, seconds: int):
        time_str = ""
        command_time = time.gmtime(seconds)
        if command_time.tm_yday - 1:
            time_str += f"{command_time.tm_yday - 1} days, "
        if command_time.tm_hour:
            time_str += f"{command_time.tm_hour} hours, "
        if command_time.tm_min:
            time_str += f"{command_time.tm_min} minutes, "
        if command_time.tm_sec:
            time_str += f"{command_time.tm_sec} seconds"

        return time_str

    def record_result(
        self,
        command: str,
        error_messages: list[str],
        warn_messages: list[str],
        skip_messages: list[str],
        done_message: str,
    ):
        command_seconds = int(
            self._command_times[command]["end"] - self._command_times[command]["start"]
        )

        log_message = ""
        if error_messages:
            log_message += ":red_circle:"
            status = "Error"
        elif warn_messages:
            log_message += ":large_orange_circle:"
            status = "Warning"
        else:
            log_message += ":large_green_circle:"
            status = "Success"

        time_str = self.seconds_to_time_string(command_seconds)
        log_message += f"Invoke dbt with `dbt {command}` ({status} in {time_str})"
        if done_message:
            log_message += f"\n*Summary*: `{done_message}`"

        if error_messages:
            log_message += "\nError messages:\n```{}```".format("\n\n".join(error_messages))

        if warn_messages:
            log_message += "\nWarning messages:\n```{}```".format("\n\n".join(warn_messages))

        if skip_messages:
            skips = [
                msg.split(" ")[5].split(".")[1]
                for msg in skip_messages
                if msg.split(" ")[4] == "relation"
            ]
            log_message += "\nSkipped:\n```{}```".format(", ".join(skips))

        self.log_messages.append(log_message)

    def send_to_slack(self) -> None:
        """Log final result to logger and send to slack."""
        end_time = time.time()
        duration_seconds = int(end_time - self.start)
        duration_time_str = self.seconds_to_time_string(duration_seconds)

        full_log_message = ""
        if any(":red_circle:" in log_message for log_message in self.log_messages):
            status = "failed"
            full_log_message += ":red_circle:"
        else:
            status = "succeeded"
            full_log_message += ":large_green_circle:"

        now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M")
        full_log_message += f"*dbt run {status} - {now}*"
        full_log_message += f"\n*Duration:* {duration_time_str}\n\n"
        full_log_message += "\n".join(self.log_messages)

        if self.slack_webhook:
            Slack.message(self.slack_channel, full_log_message, self.slack_webhook)
        elif self.slack_api_key:
            Slack(self.slack_api_key).message(self.slack_channel, full_log_message)

    def log_results(self, command_str: str, stdout: str, stderr: str) -> None:
        """Parsed logs from dbt command and log to logger and slack."""

        message = ""
        parsed_rows = []

        for output in (stdout, stderr):
            for row in output.split("\n"):
                if not row:
                    continue
                try:
                    parsed_row = json.loads(row)
                    parsed_rows.append(parsed_row)
                except json.JSONDecodeError:
                    message += row + "\n"

        log_messages = []
        error_messages = []
        warn_messages = []
        skip_messages = []

        for row in parsed_rows:
            if not row["info"]["msg"]:
                continue

            log_message = row["info"]["msg"]
            log_messages.append(log_message)

            if row["info"]["level"] == "error":
                logger.error(log_message)
                error_messages.append(log_message)
            # Capture model/test warnings but exclude verbose top-level warnings
            elif row["info"]["level"] == "warn" and "[WARNING]" not in row["info"]["msg"]:
                logger.warning(log_message)
                warn_messages.append(log_message)
            elif "SKIP " in row["info"]["msg"]:
                logger.warning(log_message)
                skip_messages.append(log_message)
            else:
                logger.info(log_message)

        done_messages = [i for i in log_messages if "Done. PASS" in i]
        if done_messages:
            done_message = done_messages[0]
        else:
            done_message = ""

        self.record_result(command_str, error_messages, warn_messages, skip_messages, done_message)


class dbtRunner:
    def __init__(
        self,
        commands: List[str],
        dbt_project_directory: pathlib.Path,
        dbt_schema: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[str] = None,
        raise_errors: bool = False,
        slack_channel: Optional[str] = None,
        slack_webhook: Optional[str] = None,
        slack_api_key: Optional[str] = None,
    ) -> None:
        """Initialize dbtRunner client with commands, credentials, and options.

        `Args:`
            commands: List[str]
                A list of strings, each string a dbt command with
                options separated by spaces.
                e.g. ["seed", "build -s models/staging", "test"]
            dbt_project_directory: pathlib.Path
                The path to find the dbt project, as a working
                directory for dbt commands to run
            dbt_schema: Optional[str]
                Populates an environment variable DBT_SCHEMA
                which can be used in your dbt profile.
                Not required if the `DBT_SCHEMA` environment variable set.
            username: Optional[str]
                Populates an environment variable REDSHIFT_USERNAME
                which can be used in your dbt profile
                Not requried if the `REDSHIFT_USERNAME`
                environment variable set.
            password: Optional[str]
                Populates an environment variable REDSHIFT_PASSWORD
                which can be used in your dbt profile
                Not requried if the `REDSHIFT_PASSWORD`
                environment variable set.
            host: Optional[str]
                Populates an environment variable REDSHIFT_HOST
                which can be used in your dbt profile
                Not requried if the `REDSHIFT_HOST`
                environment variable set.
            port: Optional[str]
                Populates an environment variable REDSHIFT_PORT
                which can be used in your dbt profile
                Not requried if the `REDSHIFT_PORT`
                environment variable set.
            db: Optional[str]
                Populates an environment variable REDSHIFT_DB
                which can be used in your dbt profile
                Not requried if the `REDSHIFT_DB`
                environment variable set.
            raise_errors: bool
                Default value: False
                A flag indicating whether errors encountered by
                the dbt command should be raised as exceptions.
            slack_channel: Optional[str]
                If set, will be used to send log results. Can be set
                with environment variable `SLACK_CHANNEL`
            slack_webhook: Optional[str]
                If set, will be used to send log results. Only one
                of slack_webhook or slack_api_key is necessary.
                Can be set with environment variable `SLACK_WEBHOOK`
            slack_api_key: Optional[str]
                If set, will be used to send log results. Only one
                of slack_webhook or slack_api_key is necessary.
                Can be set with environment variable `SLACK_API_KEY`
        """
        self.commands = commands
        self.dbt_schema = check_env.check("DBT_SCHEMA", dbt_schema)
        self.username = check_env.check("REDSHIFT_USERNAME", username)
        self.password = check_env.check("REDSHIFT_PASSWORD", password)
        self.host = check_env.check("REDSHIFT_HOST", host)
        self.port = check_env.check("REDSHIFT_PORT", port)
        self.db = check_env.check("REDSHIFT_DB", db)
        self.dbt_project_directory = dbt_project_directory
        self.raise_errors = raise_errors
        self.dbt_logger = dbtLogger(
            slack_channel=slack_channel or os.environ.get("SLACK_CHANNEL"),
            slack_webhook=slack_webhook or os.environ.get("SLACK_WEBHOOK"),
            slack_api_key=slack_api_key or os.environ.get("SLACK_API_KEY"),
        )

    def run(self) -> None:
        for command in self.commands:
            self.dbt_command(command)
        self.dbt_logger.send_to_slack()

    def dbt_command(self, command: str) -> None:
        """Runs dbt command and logs results after process is completed.

        If raise_error is set, this method will raise an error if the dbt
        command hits any errors.
        """

        self.dbt_logger.record_start(command)
        dbt_executable_path = shutil.which("dbt")
        commands = [dbt_executable_path, "--log-format", "json"] + command.split(" ")

        shell_environment = {
            "REDSHIFT_USERNAME": self.username,
            "REDSHIFT_PASSWORD": self.password,
            "REDSHIFT_HOST": self.host,
            "REDSHIFT_PORT": self.port,
            "REDSHIFT_DB": self.db,
            "DBT_SCHEMA": self.dbt_schema,
        }

        process = subprocess.run(
            commands,
            env=shell_environment,
            cwd=self.dbt_project_directory,
            text=True,
            capture_output=True,
        )
        self.dbt_logger.record_end(command)

        self.dbt_logger.log_results(command, process.stdout, process.stderr)

        if self.raise_errors:
            process.check_returncode()
