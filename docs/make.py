"""Build multi-version Sphinx documentation."""

import logging
import shutil
import subprocess
import sys
from pathlib import Path

from packaging import version

ROOT_DIR = Path(__file__).resolve().parent.parent
SPHINXBUILD = "sphinx-build"
SOURCEDIR = ROOT_DIR / "docs"
BUILDDIR = SOURCEDIR / "_build"
HTMLDIR = SOURCEDIR / "html"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def check_dependencies():
    """Verify that the required CLI tools are installed and available in the system PATH."""
    tools = ["git", SPHINXBUILD, "sphinx-multiversion"]
    for tool in tools:
        logger.debug("Checking PATH for %s.", tool)
        if not shutil.which(tool):
            logger.error("Required tool '%s' not found in PATH.", tool)
            sys.exit(1)
    logger.debug("All required tools found in PATH.")


def run_command(
    command: list[str | Path], cwd: Path = ROOT_DIR, *, verbose: bool = False
) -> subprocess.CompletedProcess:
    """Execute a shell command with error handling and output capture."""
    cmd_str = [str(arg) for arg in command]
    try:
        return subprocess.run(cmd_str, cwd=cwd, check=True, capture_output=verbose, text=True)
    except subprocess.CalledProcessError as e:
        logger.error("Command failed: %s", " ".join(cmd_str))
        if not verbose and e.stderr:
            logger.error("Details: %s", e.stderr.strip())
        sys.exit(e.returncode)


def reuse_builds_old_versions(keep_older_than: str | None = None):
    """Remove folders not starting with 'v' or with a version >= ``keep_older_than``, if provided."""
    if not HTMLDIR.exists():
        return

    generate_after = version.parse(keep_older_than) if keep_older_than else None

    for item in HTMLDIR.iterdir():
        if not item.is_dir():
            logger.info("Removing non-directory file %s.", item)
            item.unlink()
            continue

        if not item.name.startswith("v"):
            logger.info("Removing non-version folder: %s", item.name)
            shutil.rmtree(item)
            continue

        try:
            item_ver = version.parse(item.name.lstrip("v"))
            if not generate_after or item_ver >= generate_after:
                logger.info("Removing build files for version: %s", item.name)
                shutil.rmtree(item)
        except version.InvalidVersion:
            logger.warning("Removing build files for invalid version: %s", item.name)
            shutil.rmtree(item)


def clean():
    """Delete the '_build' and 'html' directories if they exist."""
    for d in [BUILDDIR, HTMLDIR]:
        if d.exists():
            logger.info("Deleting build files from %s...", d)
            shutil.rmtree(d)
        logger.debug("Directory %s not found.", d)


def test():
    """Build sphinx documentation from latest code failing if there are syntax issues."""
    check_dependencies()

    logger.info("Building single-version docs with strict syntax and reference checks.")
    run_command(
        [
            SPHINXBUILD,
            "--jobs=auto",
            "--fail-on-warning",
            "--nitpicky",
            "--fresh-env",
            SOURCEDIR,
            BUILDDIR / "html_test",
        ],
        verbose=True,
    )


def linkcheck():
    """Build sphinx documentation, checking for broken links."""
    check_dependencies()

    logger.info("Building single-version docs, checking all links for validity.")
    run_command(
        [SPHINXBUILD, "--builder", "linkcheck", SOURCEDIR, BUILDDIR / "linkcheck"], verbose=True
    )


def build():
    """Build multi-version sphinx documentation."""
    check_dependencies()

    logger.info("Re-using any existing builds with versions before v5.0.0.")
    reuse_builds_old_versions(keep_older_than="v5.0.0")

    git_base = ["git", "-C", ROOT_DIR]

    logger.info("Mapping `latest` to current directory...")
    run_command([*git_base, "branch", "-f", "latest"])

    tag_proc = run_command([*git_base, "tag", "-l", "--sort=-v:refname"])
    tags = tag_proc.stdout.strip().split("\n")

    if tags and tags[0]:
        stable_tag = tags[0]
        logger.info("Mapping 'stable' to %s", stable_tag)
        run_command([*git_base, "branch", "-f", "stable", stable_tag])
    else:
        logger.warning("No tags found. Mapping 'stable' to 'latest'.")
        run_command([*git_base, "branch", "-f", "stable", "latest"])

    logger.info("Building multiversion documentation...")
    run_command(["sphinx-multiversion", SOURCEDIR, HTMLDIR])

    src_redirect = SOURCEDIR / "index-redirect.html"
    if src_redirect.exists():
        shutil.copy2(src_redirect, HTMLDIR / "index.html")
        logger.info("Static redirect applied to root.")

    src_404 = SOURCEDIR / "404.html"
    if src_404.exists():
        shutil.copy2(src_404, HTMLDIR / "404.html")
        logger.info("404 page applied to root.")


if __name__ == "__main__":
    targets = {
        "clean": clean,
        "test": test,
        "linkcheck": linkcheck,
        "build_docs": build,
        "help": lambda: run_command([SPHINXBUILD, "--help"]),
    }

    target = sys.argv[1] if len(sys.argv) > 1 else "help"

    if target in targets:
        targets[target]()
    else:
        run_command([SPHINXBUILD, "-M", target, SOURCEDIR, BUILDDIR], verbose=True)
