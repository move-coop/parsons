from collections.abc import Callable
from pathlib import Path

import pytest
import yaml
from dbt.artifacts.schemas.results import NodeResult

from parsons.utilities.dbt.dbt import run_dbt_commands
from parsons.utilities.dbt.logging import dbtLogger

# Base dbt profile configurations
CONNECTOR_CONFIGS = {
    "duckdb": {"type": "duckdb", "path": "{project_dir}/test.duckdb"},
}


def write_yaml(path: Path, data: dict) -> None:
    """
    Write a dictionary to a YAML file at the specified path.

    Args:
        path: The filesystem path where the YAML file should be created.
        data: The dictionary content to serialize into YAML.

    """
    with path.open("w") as f:
        yaml.dump(data, f)


def resolve_config(config: dict, project_dir: Path) -> dict:
    """
    Recursively replace placeholders in the config dictionary.

    Scan the dictionary for string values and apply `.format()` using
    available context (e.g., project_dir). Allows connector-specific
    paths to be relative to the temporary test environment.

    Args:
        config: The raw connector configuration dictionary.
        project_dir: The Path object to inject into placeholders.

    Returns:
        A new dictionary with all string placeholders resolved.

    """
    resolved = {}
    for k, v in config.items():
        if isinstance(v, str):
            resolved[k] = v.format(project_dir=project_dir)
        elif isinstance(v, dict):
            resolved[k] = resolve_config(v, project_dir)
        else:
            resolved[k] = v
    return resolved


def setup_dbt_files(proj_dir: Path, prof_dir: Path, connector_type: str) -> None:
    """
    Initialize a minimal dbt project structure on the filesystem.

    Creates the `dbt_project.yml`, `profiles.yml`, and a dummy model file
    required to execute dbt commands. The profile is dynamically generated
    based on the provided connector type.

    Args:
        proj_dir: Path to the dbt project root directory.
        prof_dir: Path to the directory where profiles.yml should reside.
        connector_type: The key for the desired connector in CONNECTOR_CONFIGS.

    Raises:
        KeyError: If connector_type does not exist in CONNECTOR_CONFIGS.

    """
    raw_config = CONNECTOR_CONFIGS[connector_type]
    target_config = resolve_config(raw_config, proj_dir)

    write_yaml(
        proj_dir / "dbt_project.yml",
        {
            "name": "e2e_test",
            "version": "1.0.0",
            "config-version": 2,
            "profile": "parsons_profile",
            "model-paths": ["models"],
        },
    )

    write_yaml(
        prof_dir / "profiles.yml",
        {
            "parsons_profile": {
                "outputs": {"dev": target_config},
                "target": "dev",
            }
        },
    )

    models_dir = proj_dir / "models"
    models_dir.mkdir(exist_ok=True)
    (models_dir / "dummy_model.sql").write_text("SELECT 1 as id")


@pytest.fixture
def dbt_env_factory(tmp_path: Path) -> Callable[[str], tuple[Path, Path]]:
    """
    Lazily initialize a dbt project for a specific adapter
    (e.g., Redshift, Postgres) within a unique temporary directory.

    Args:
        tmp_path: Built-in pytest fixture for temporary directory management.

    Returns:
        Callable[[str], tuple[Path, Path]]:
            Take a connector_type string and return a tuple of
            (project_directory, profile_directory).

    """

    def _setup(connector_type: str) -> tuple[Path, Path]:
        """
        Take a connector_type string and return a tuple of
        (project_directory, profile_directory).
        """
        proj_dir = tmp_path / f"project_{connector_type}"
        prof_dir = tmp_path / f"profiles_{connector_type}"
        proj_dir.mkdir(parents=True)
        prof_dir.mkdir(parents=True)

        setup_dbt_files(proj_dir, prof_dir, connector_type)
        return proj_dir, prof_dir

    return _setup


@pytest.mark.parametrize("connector", ["duckdb"])
def test_run_dbt_commands_e2e(
    connector: str, dbt_env_factory: Callable[[str], tuple[Path, Path]]
) -> None:
    """
    Verify that dbt commands execute successfully across different database connectors.

    Args:
        connector: The database adapter to test (parameterized).
        dbt_env_factory: The factory fixture to generate the project files.

    """
    project_dir, profile_dir = dbt_env_factory(connector)

    results = run_dbt_commands(
        commands=["run"], dbt_project_directory=project_dir, dbt_profile_directory=profile_dir
    )

    assert len(results) == 1
    assert results[0].overall_status == "success"

    target_dir = project_dir / "target"
    assert (target_dir / "manifest.json").exists()
    assert (target_dir / "run_results.json").exists()

    model_names = [r.node.name for r in results[0].results]
    assert "dummy_model" in model_names

    for result in results[0].results:
        assert isinstance(result, NodeResult)
        assert result.status == "success", f"Model {result.node.name} failed with {result.message}"


def test_logger_integration(dbt_env_factory: Callable[[str], tuple[Path, Path]], mocker) -> None:
    """
    Tests that the dbtLogger correctly captures and sends events during command execution.

    Args:
        dbt_env_factory: The factory fixture to generate the project files.
        mocker: The pytest-mock fixture for spying on the logger.

    """
    # Initialize a default environment (using duckdb for speed)
    project_dir, profile_dir = dbt_env_factory("duckdb")
    mock_logger = mocker.Mock(spec=dbtLogger)

    run_dbt_commands(
        commands=["run"],
        dbt_project_directory=project_dir,
        dbt_profile_directory=profile_dir,
        loggers=[mock_logger],
    )

    mock_logger.send.assert_called_once()
