"""
Check before.txt and after.txt to ensure the right packages have been installed.

The txt files are outputs of uv pip freeze before and after installing a parsons extra using PARSONS_LIMITED_DEPENDENCIES.
"""

import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from setup import CORE_DEPENDENCIES, EXTRA_DEPENDENCIES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def main(extra: str) -> None:
    if extra not in EXTRA_DEPENDENCIES:
        logger.error(f"Unknown extra: '{extra}'")
        logger.info(f"Available extras: {', '.join(EXTRA_DEPENDENCIES.keys())}")
        sys.exit(1)

    required = CORE_DEPENDENCIES + EXTRA_DEPENDENCIES[extra]
    required_packages = list({extract_package_name(dep).lower() for dep in required})

    before = {line.strip() for line in Path("before.txt").read_text().splitlines() if line.strip()}
    after = {line.strip() for line in Path("after.txt").read_text().splitlines() if line.strip()}

    newly_installed = after - before

    logger.info("#### Newly installed packages ####")
    for pkg in sorted(newly_installed):
        logger.debug(pkg)

    logger.info("\n### Checking required packages ###")
    missing = []
    for required_dep, required_pkg in zip(required, required_packages):
        found = any(pkg.lower().startswith(f"{required_pkg}==") for pkg in newly_installed)
        if found:
            logger.debug(f"✓ {required_pkg}")
        else:
            logger.warning(f"✗ {required_pkg} (from: {required_dep}) (not in newly installed)")
            missing.append(required_pkg)

    if missing:
        logger.error(f"\n✗ Missing packages: {', '.join(missing)}")
        sys.exit(1)
    else:
        logger.info("\n✓ All required packages were installed!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python script.py <extra_name>")
        logger.info("Example: python script.py airtable")
        sys.exit(1)

    main(sys.argv[1])
