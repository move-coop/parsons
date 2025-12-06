"""
Check before.txt and after.txt to ensure the right packages have been installed.

The txt files are outputs of uv pip freeze before and after installing a parsons extra using PARSONS_LIMITED_DEPENDENCIES.
"""

import logging
import re
import sys
from itertools import chain
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from setup import CORE_DEPENDENCIES, EXTRA_DEPENDENCIES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvalidExtraError(ValueError):
    """Raised when an invalid extra name is provided."""

    def __init__(self, extra: str):
        self.extra = extra
        available = ", ".join(list(EXTRA_DEPENDENCIES.keys()) + ["all"])
        super().__init__(f"Unknown extra: '{extra}'. Available extras: {available}")


class MissingPackagesError(Exception):
    """Raised when required packages are not installed."""

    def __init__(self, missing_packages: list[str]):
        self.missing_packages = missing_packages
        super().__init__(f"✗ Missing packages: {', '.join(missing_packages)}")


def extract_package_name(dependency_spec: str) -> str:
    """
    Extract the package name from a dependency specification.

    Split on version operators and environment markers
    Package name is everything before the first space, comparison operator, or semicolon

    Examples:
    'requests' -> 'requests'
    'psycopg2-binary <= 2.9.9;python_version<"3.13"' -> 'psycopg2-binary'
    'sqlalchemy >= 1.4.22, != 1.4.33, < 3.0.0' -> 'sqlalchemy'
    """
    match = re.match(r"^([a-zA-Z0-9_-]+)", dependency_spec.strip())
    return match.group(1) if match else dependency_spec.strip()


def validate_extra(extra: str) -> None:
    """Validate that the extra name is valid."""
    if extra != "all" and extra not in EXTRA_DEPENDENCIES:
        raise InvalidExtraError(extra)


def get_required_dependencies(extra: str) -> list[str]:
    """Get the list of required dependencies for the given extra."""
    if extra != "all":
        return CORE_DEPENDENCIES + EXTRA_DEPENDENCIES[extra]
    all_deps = list(chain.from_iterable(EXTRA_DEPENDENCIES.values()))
    return CORE_DEPENDENCIES + all_deps


def get_newly_installed_packages() -> set[str]:
    """Load the before and after package sets and return a set of the packages that were installed."""
    before = {line.strip() for line in Path("before.txt").read_text().splitlines() if line.strip()}
    after = {line.strip() for line in Path("after.txt").read_text().splitlines() if line.strip()}
    newly_installed = after - before

    logger.info("#### Newly installed packages ####")
    for pkg in sorted(newly_installed):
        logger.debug(pkg)

    return newly_installed


def verify_required_packages(required: list[str], newly_installed: set[str]) -> None:
    """
    Verify that all required packages were installed.

    Raises MissingPackagesError if any packages are missing.
    """
    required_packages = list({extract_package_name(dep).lower() for dep in required})

    logger.info("### Checking required packages ###")
    missing = []

    for required_dep, required_pkg in zip(required, required_packages):
        found = any(pkg.lower().startswith(f"{required_pkg}==") for pkg in newly_installed)
        if found:
            logger.debug("✓ %s", required_pkg)
            continue
        logger.warning("✗ %s (from: %s) (not in newly installed)", required_pkg, required_dep)
        missing.append(required_pkg)

    if missing:
        raise MissingPackagesError(missing)


def main(extra: str) -> None:
    validate_extra(extra)

    required = get_required_dependencies(extra)
    newly_installed = get_newly_installed_packages()
    verify_required_packages(required, newly_installed)

    logger.info("✓ All required packages were installed!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python script.py <extra_name>")
        logger.info("Example: python script.py airtable")
        sys.exit(1)

    try:
        main(sys.argv[1])
    except (InvalidExtraError, MissingPackagesError) as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred: %s", str(e))
        sys.exit(1)
