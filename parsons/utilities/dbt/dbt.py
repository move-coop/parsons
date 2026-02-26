"""Core methods for running dbt commands."""

import logging
from pathlib import Path

from dbt.cli.main import dbtRunner, dbtRunnerResult

from parsons.utilities.dbt.logging import dbtLogger
from parsons.utilities.dbt.models import Manifest

logger = logging.getLogger(__name__)


class dbtRunnerParsons:
    def __init__(
        self,
        commands: str | list[str],
        dbt_project_directory: Path,
        dbt_profile_directory: Path | None = None,
    ) -> None:
        """Initialize dbtRunner with commands and a working directory.

        Args:
            commands: Union[str, list[str]]
                A single dbt command string or a list of dbt command
                strings.
                e.g. ["seed", "build -s models/staging", "test"]
            dbt_project_directory: Path
                The path to find the dbt project, as a working
                directory for dbt commands to run
            dbt_profile_directory: Path, optional
                The path to find the dbt profile

        """
        if isinstance(commands, str):
            commands = [commands]
        self.commands = commands
        self.dbt_project_directory = dbt_project_directory
        self.dbt_profile_directory = dbt_profile_directory

    def run(self) -> list[Manifest]:
        """Executes dbt commands one by one, returns all results."""
        results = []

        for command in self.commands:
            result = self.execute_dbt_command(command)
            if result.run_execution_result:
                results.append(result)

        return results

    def execute_dbt_command(self, command: str) -> Manifest:
        """Runs dbt command and logs results after process is completed."""
        if command.startswith("dbt "):
            command = command[4:]

        # initialize
        dbt = dbtRunner()

        # create CLI args as a list of strings
        cli_args = command.split(" ")
        cli_args.extend(["--project-dir", str(self.dbt_project_directory)])
        if self.dbt_profile_directory:
            cli_args.extend(["--profiles-dir", str(self.dbt_profile_directory)])

        # run the command
        result: dbtRunnerResult = dbt.invoke(cli_args)
        if result.exception:
            raise result.exception

        return Manifest(command=command, run_execution_result=result.result)


def run_dbt_commands(
    commands: str | list[str],
    dbt_project_directory: Path,
    dbt_profile_directory: Path | None = None,
    loggers: list[dbtLogger | type[dbtLogger]] | None = None,
) -> list[Manifest]:
    """Executes dbt commands within a directory, optionally logs results.

    .. code-block:: python

        from pathlib import Path
        from parsons.utilities.dbt import (
            run_dbt_commands,
            dbtLoggerSlack,
            dbtLoggerPython
        )
        results = run_dbt_commands(
            commands=["dbt run", "dbt test"],
            dbt_project_directory=Path("/path/to/dbt/project"),
            loggers=[dbtLoggerPython, dbtLoggerSlack]
        )

    Args:
        commands : Union[str, list[str]]
            A single dbt command as a string or a list of dbt commands to
            be executed.
        dbt_project_directory : Path
            The path to the dbt project directory where the commands will
            be executed.
        dbt_profile_directory: Path, optional
            The path to find the dbt profile
        loggers : Optional[list[Union[dbtLogger, Type[dbtLogger]]]], default=None
            A list of logger instances or logger classes. If classes are
            provided, they will be instantiated.  Each logger should have
            a `send` method that takes the dbt command results as an
            argument.

    Returns:
        list[Manifest]
            A list of result objects from the executed dbt commands.

    """
    dbt_runner = dbtRunnerParsons(
        commands=commands,
        dbt_project_directory=dbt_project_directory,
        dbt_profile_directory=dbt_profile_directory,
    )

    dbt_command_results = dbt_runner.run()

    if loggers:
        for dbt_logger in loggers:
            if not isinstance(dbt_logger, dbtLogger):
                # Instantiate logger if not already instantiated
                dbt_logger = dbt_logger()
            dbt_logger.send(dbt_command_results)

    return dbt_command_results
