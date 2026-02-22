from pathlib import Path

import pytest
import yaml

from parsons.utilities.dbt.dbt import run_dbt_commands
from parsons.utilities.dbt.logging import dbtLogger


def write_yaml(path: Path, data: dict):
    with path.open("w") as f:
        yaml.dump(data, f)


def setup_dbt_files(proj_dir: Path, prof_dir: Path) -> None:
    """Encapsulates all file system setup for a dbt project."""
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
                "outputs": {"dev": {"type": "duckdb", "path": str(proj_dir / "test.duckdb")}},
                "target": "dev",
            }
        },
    )

    # Models
    models_dir = proj_dir / "models"
    models_dir.mkdir()
    (models_dir / "dummy_model.sql").write_text("SELECT 1 as id")


@pytest.fixture
def dbt_env(tmp_path: Path) -> tuple[Path, Path]:
    proj_dir = tmp_path / "project"
    prof_dir = tmp_path / "profiles"
    proj_dir.mkdir()
    prof_dir.mkdir()

    setup_dbt_files(proj_dir, prof_dir)
    return proj_dir, prof_dir


def test_run_dbt_commands_e2e(dbt_env: tuple[Path, Path]) -> None:
    project_dir, profile_dir = dbt_env

    results = run_dbt_commands(
        commands=["run"], dbt_project_directory=project_dir, dbt_profile_directory=profile_dir
    )

    assert len(results) == 1
    manifest = results[0]

    assert manifest.overall_status == "success"

    assert manifest.summary.get("success", 0) + manifest.summary.get("Success", 0) == 1


def test_logger_integration(dbt_env: tuple[Path, Path], mocker) -> None:
    project_dir, profile_dir = dbt_env
    mock_logger = mocker.Mock(spec=dbtLogger)

    run_dbt_commands(
        commands=["run"],
        dbt_project_directory=project_dir,
        dbt_profile_directory=profile_dir,
        loggers=[mock_logger],
    )

    mock_logger.send.assert_called_once()
