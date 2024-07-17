"""Core methods for running dbt commands."""

import json
import logging
import time
import os
import pathlib
import shutil
import subprocess
from typing import List, Optional, Type, Union

from parsons.utilities.dbt.logging import dbtLogger
from parsons.utilities.dbt.models import dbtCommandResult

logger = logging.getLogger(__name__)


class dbtRunner:
    def __init__(
        self,
        commands: Union[str, List[str]],
        dbt_project_directory: pathlib.Path,
    ) -> None:
        """Initialize dbtRunner with commands and a working directory.

        `Args:`
            commands: Union[str, List[str]]
                A single dbt command string or a list of dbt command
                strings.
                e.g. ["seed", "build -s models/staging", "test"]
            dbt_project_directory: pathlib.Path
                The path to find the dbt project, as a working
                directory for dbt commands to run
        """
        if isinstance(commands, str):
            commands = [commands]
        self.commands = commands
        self.dbt_project_directory = dbt_project_directory

    def run(self) -> list[dbtCommandResult]:
        """Executes dbt commands one by one, returns all results."""
        results = []

        for command in self.commands:
            result = self.execute_dbt_command(command)
            results.append(result)

        return results

    def execute_dbt_command(self, command: str) -> dbtCommandResult:
        """Runs dbt command and logs results after process is completed.

        If raise_error is set, this method will raise an error if the dbt
        command hits any errors.
        """
        if command.startswith("dbt "):
            command = command[4:]
        dbt_executable_path = shutil.which("dbt")
        if not dbt_executable_path:
            raise RuntimeError("dbt executable not found.")

        commands = [dbt_executable_path, "--log-format", "json"] + command.split(" ")

        completed_process = subprocess.run(
            commands,
            env=os.environ.copy(),
            cwd=self.dbt_project_directory,
            text=True,
            capture_output=True,
        )

        logger.debug(completed_process.stdout)
        logger.debug(completed_process.stderr)

        if completed_process.returncode == 2:
            raise RuntimeError(completed_process.stderr)

        run_results_filepath = os.path.join(
            self.dbt_project_directory, "target", "run_results.json"
        )
        if not os.path.exists(run_results_filepath):
            # Sometimes it takes a few seconds for this file to materialize
            time.sleep(5)
        with open(run_results_filepath) as file:
            raw_result = json.loads(file.read())

        result = dbtCommandResult(command=command, **raw_result)

        return result


def run_dbt_commands(
    commands: Union[str, List[str]],
    dbt_project_directory: pathlib.Path,
    loggers: Optional[list[Union[dbtLogger, Type[dbtLogger]]]] = None,
) -> list[dbtCommandResult]:
    """Executes dbt commands within a directory, optionally logs results.

    Parameters:
    -----------
    commands : Union[str, List[str]]
        A single dbt command as a string or a list of dbt commands to
        be executed.

    dbt_project_directory : pathlib.Path
        The path to the dbt project directory where the commands will
        be executed.

    loggers : Optional[list[Union[dbtLogger, Type[dbtLogger]]]], default=None
        A list of logger instances or logger classes. If classes are
        provided, they will be instantiated.  Each logger should have
        a `send` method that takes the dbt command results as an
        argument.

    Returns:
    --------
    list[dbtCommandResult]
        A list of result objects from the executed dbt commands.

    Example:
    --------
    >>> from pathlib import Path
    >>> from parsons.utilities.dbt import (
    ...     run_dbt_commands,
    ...     dbtLoggerSlack,
    ...     dbtLoggerPython
    ... )
    >>> results = run_dbt_commands(
    ...     commands=["dbt run", "dbt test"],
    ...     dbt_project_directory=Path("/path/to/dbt/project"),
    ...     loggers=[dbtLoggerPython, dbtLoggerSlack]
    ... )
    """
    dbt_runner = dbtRunner(commands, dbt_project_directory)

    dbt_command_results = dbt_runner.run()

    if loggers:
        for logger in loggers:
            if not isinstance(logger, dbtLogger):
                # Instantiate logger if not already instantiated
                logger = logger()
            logger.send(dbt_command_results)

    return dbt_command_results
