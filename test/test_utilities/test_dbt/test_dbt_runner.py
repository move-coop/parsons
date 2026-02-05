"""
Tests for the dbtRunnerParsons wrapper class.

Tests the core functionality of the dbtRunnerParsons wrapper,
focusing on command execution, argument parsing, and integration
with the dbt-core Python API.
"""

from unittest.mock import Mock, patch

from parsons.utilities.dbt.dbt import dbtRunnerParsons


class TestDbtRunnerParsons:
    """Test suite for the dbtRunnerParsons wrapper class."""

    @patch("parsons.utilities.dbt.dbt.dbtRunner")
    def test_execute_dbt_command_strips_dbt_prefix(self, mock_runner_class, tmp_path):
        """
        Verify that execute_dbt_command removes 'dbt' prefix from CLI commands.

        The dbt Python API expects command arguments without the 'dbt' prefix
        (e.g., ['run'] instead of ['dbt', 'run']). This test ensures the wrapper
        properly strips the prefix when present.
        """
        mock_runner_inst = mock_runner_class.return_value
        mock_runner_inst.invoke.return_value = Mock(result=Mock(), exception=None)

        runner = dbtRunnerParsons(commands="dbt run", dbt_project_directory=tmp_path)
        runner.execute_dbt_command("dbt run")

        args = mock_runner_inst.invoke.call_args[0][0]
        assert "dbt" not in args, "Command should not contain 'dbt' prefix"
        assert "run" in args, "Command should contain 'run' argument"

    @patch("parsons.utilities.dbt.dbt.dbtRunner")
    def test_execute_dbt_command_adds_project_directory(self, mock_runner_class, tmp_path):
        """
        Verify that execute_dbt_command injects --project-dir argument.

        The wrapper should automatically add the --project-dir flag with the
        configured directory path to every command execution.
        """
        mock_runner_inst = mock_runner_class.return_value
        mock_runner_inst.invoke.return_value = Mock(result=Mock(), exception=None)

        runner = dbtRunnerParsons(commands="run", dbt_project_directory=tmp_path)
        runner.execute_dbt_command("run")

        args = mock_runner_inst.invoke.call_args[0][0]
        assert "--project-dir" in args, "Command should include --project-dir flag"
        assert str(tmp_path) in args, "Command should include project directory path"

    @patch("parsons.utilities.dbt.dbt.dbtRunner")
    def test_execute_dbt_command_handles_commands_without_prefix(self, mock_runner_class, tmp_path):
        """
        Verify that commands without 'dbt' prefix are handled correctly.

        Users may provide commands with or without the 'dbt' prefix. This test
        ensures both formats work correctly.
        """
        mock_runner_inst = mock_runner_class.return_value
        mock_runner_inst.invoke.return_value = Mock(result=Mock(), exception=None)

        runner = dbtRunnerParsons(commands="run", dbt_project_directory=tmp_path)
        runner.execute_dbt_command("run")

        args = mock_runner_inst.invoke.call_args[0][0]
        assert "run" in args, "Command should contain 'run' argument"
        assert args.count("run") == 1, "Command should only contain 'run' once"
