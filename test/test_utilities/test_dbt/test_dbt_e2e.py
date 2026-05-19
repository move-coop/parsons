from pathlib import Path

import pytest
import yaml
from dbt.artifacts.schemas.results import NodeResult

from parsons.utilities.dbt.dbt import run_dbt_commands
from parsons.utilities.dbt.logging import dbtLogger


def write_yaml(path: Path, data: dict) -> None:
    """
    Write a dictionary to a YAML file at the specified path.

    Args:
        path: The filesystem path where the YAML file should be created.
        data: The dictionary content to serialize into YAML.

    """
    path.write_text(yaml.dump(data))


def resolve_config(config: dict[str, str | dict], project_dir: Path) -> dict[str, str]:
    """
    Recursively replace placeholders in the config dictionary.

    Scan the dictionary for string values and apply `.format()` using
    available context (e.g., project_dir). Allows adapter-specific
    paths to be relative to the temporary test environment.

    Args:
        config: The raw adapter configuration dictionary.
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


def setup_dbt_files(proj_dir: Path, prof_dir: Path, adapter_type: str, adapter_path: str) -> None:
    """
    Initialize a minimal dbt project structure on the filesystem.

    Creates the `dbt_project.yml`, `profiles.yml`, and a dummy model file
    required to execute dbt commands. The profile is dynamically generated
    based on the provided adapter type.

    Args:
        proj_dir: Path to the dbt project root directory.
        prof_dir: Path to the directory where profiles.yml should reside.
        adapter_type: The name of the desired adapter.
        adapter_path: The path for the desired adapter.

    """
    target_config = resolve_config({"type": adapter_type, "path": adapter_path}, proj_dir)

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


@pytest.fixture(
    params=[
        {"type": "duckdb", "path": "{project_dir}/test.duckdb"},
    ],
    ids=[
        "duckdb",
    ],
)
def dbt_env(request, tmp_path: Path) -> tuple[Path, Path]:
    """Parameterized fixture that sets up a dbt environment for each adapter."""
    config = request.param
    adapter_type = config["type"]
    adapter_path = config["path"]

    # Unique directories per adapter to avoid collision
    proj_dir = tmp_path / f"project_{adapter_type}"
    prof_dir = tmp_path / f"profiles_{adapter_type}"
    proj_dir.mkdir(parents=True)
    prof_dir.mkdir(parents=True)

    setup_dbt_files(proj_dir, prof_dir, adapter_type, adapter_path)

    return proj_dir, prof_dir


def test_run_dbt_commands_e2e(dbt_env: tuple[Path, Path]) -> None:
    """
    Verify that dbt commands execute successfully across different database adapters.

    Args:
        dbt_env: The factory fixture to generate the project files.

    """
    project_dir, profile_dir = dbt_env

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


def test_logger_integration(dbt_env: tuple[Path, Path], mocker) -> None:
    """
    Tests that the dbtLogger correctly captures and sends events during command execution.

    Args:
        dbt_env: The factory fixture to generate the project files.
        mocker: The pytest-mock fixture for spying on the logger.

    """
    project_dir, profile_dir = dbt_env
    mock_logger = mocker.Mock(spec=dbtLogger)

    run_dbt_commands(
        commands=["run"],
        dbt_project_directory=project_dir,
        dbt_profile_directory=profile_dir,
        loggers=[mock_logger],
    )

    mock_logger.send.assert_called_once()
