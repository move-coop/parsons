from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from dbt.artifacts.schemas.run import RunExecutionResult
from dbt.cli.exceptions import DbtInternalException

from parsons.utilities.dbt.dbt import dbtRunnerParsons


class TestDbtRunnerParsons:
    """Test suite for the dbtRunnerParsons wrapper class."""

    @pytest.mark.parametrize(
        ("input_cmd", "expected_cmd_start", "first_injected_flag"),
        [
            ("dbt run", "run", 1),
            ("run", "run", 1),
            ("dbt test --select model_a", "test", 3),
        ],
    )
    @patch("parsons.utilities.dbt.dbt.dbtRunner", autospec=True)
    def test_execute_dbt_command_args_construction(
        self,
        mock_runner_class,
        tmp_path: Path,
        input_cmd: str,
        expected_cmd_start: str,
        first_injected_flag: int,
        run_execution_result_factory: Callable[..., RunExecutionResult],
    ):
        """Verify CLI string is correctly tokenized and flags are injected."""
        # Setup the mock dbtRunner.invoke return value
        mock_runner_inst = mock_runner_class.return_value

        # We use our factory to create a REAL RunExecutionResult
        # because the Manifest class expects it.
        mock_execution_data = run_execution_result_factory()
        mock_runner_inst.invoke.return_value = MagicMock(result=mock_execution_data, exception=None)

        profile_path = Path("/path/to/profiles")

        runner = dbtRunnerParsons(
            commands=input_cmd,
            dbt_project_directory=tmp_path,
            dbt_profile_directory=profile_path,
        )

        manifest = runner.execute_dbt_command(input_cmd)

        actual_args = mock_runner_inst.invoke.call_args[0][0]

        # Assertions for prefix removal and command
        assert "dbt" not in actual_args
        assert actual_args[0] == expected_cmd_start

        # Assertions for injected flags
        assert actual_args[first_injected_flag] == "--project-dir"
        assert actual_args[first_injected_flag + 1] is str(tmp_path)
        assert actual_args[first_injected_flag + 2] == "--profiles-dir"
        assert actual_args[first_injected_flag + 3] is str(profile_path)

        # Verify Manifest was created correctly
        assert manifest.run_execution_result == mock_execution_data

    @patch("parsons.utilities.dbt.dbt.dbtRunner", autospec=True)
    def test_execute_dbt_command_raises_exception(self, mock_runner_class, tmp_path: Path):
        """Verify that dbtRunnerResult.exception is raised if it exists."""
        mock_runner_inst = mock_runner_class.return_value
        mock_runner_inst.invoke.return_value = MagicMock(
            result=None, exception=DbtInternalException("dbt profile not found")
        )

        runner = dbtRunnerParsons(commands="run", dbt_project_directory=tmp_path)

        with pytest.raises(DbtInternalException, match="dbt profile not found"):
            runner.execute_dbt_command("run")
