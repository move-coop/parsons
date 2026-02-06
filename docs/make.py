"""Build multi-version Sphinx documentation."""

import logging
import shutil
import subprocess
import sys
from pathlib import Path

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
        if not shutil.which(tool):
            logger.error("Required tool '%s' not found in PATH.", tool)
            sys.exit(1)


def run_command(command: list[str | Path], cwd: Path = ROOT_DIR) -> subprocess.CompletedProcess:
    """Execute a shell command with error handling and output capture."""
    cmd_str = [str(arg) for arg in command]
    try:
        return subprocess.run(cmd_str, cwd=cwd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error("Command failed: %s", " ".join(cmd_str))
        if e.stderr:
            logger.error("Details: %s", e.stderr.strip())
        sys.exit(e.returncode)


def build_docs():
    """Build multi-version sphinx documentation."""
    check_dependencies()

    if HTMLDIR.exists():
        shutil.rmtree(HTMLDIR)

    git_base = ["git", "-C", str(ROOT_DIR)]

    is_shallow = (ROOT_DIR / ".git" / "shallow").exists()
    if is_shallow:
        logger.warning("Shallow clone detected. Unshallowing for proper versioning...")
        run_command([*git_base, "fetch", "--unshallow", "--tags"])

    logger.info("Updating local branch references...")
    run_command([*git_base, "branch", "-f", "latest"])

    tag_proc = run_command([*git_base, "tag", "-l", "--sort=-v:refname"])
    tags = tag_proc.stdout.strip().split("\n")

    if tags and tags[0]:
        stable_tag = tags[0]
        logger.info("Stable version identified: %s", stable_tag)
        run_command([*git_base, "branch", "-f", "stable", stable_tag])
    else:
        logger.info("No tags found. Mapping 'stable' to 'latest'.")
        run_command([*git_base, "branch", "-f", "stable", "latest"])

    logger.info("Building multiversion documentation...")
    run_command(["sphinx-multiversion", str(SOURCEDIR), str(HTMLDIR)])

    redirect_src = ROOT_DIR / "index-redirect.html"
    if redirect_src.exists():
        shutil.copy2(redirect_src, HTMLDIR / "index.html")
        logger.info("Static redirect applied to root index.")


def clean():
    """Delete the '_build' and 'html' directories if they exist."""
    for d in [BUILDDIR, HTMLDIR]:
        if d.exists():
            logger.info("Cleaning %s...", d)
            shutil.rmtree(d)


if __name__ == "__main__":
    targets = {
        "build_docs": build_docs,
        "clean": clean,
        "linkcheck": lambda: run_command(
            [SPHINXBUILD, "-b", "linkcheck", SOURCEDIR, BUILDDIR / "linkcheck"]
        ),
        "help": lambda: run_command([SPHINXBUILD, "-M", "help", SOURCEDIR, BUILDDIR]),
    }

    target = sys.argv[1] if len(sys.argv) > 1 else "help"

    if target in targets:
        targets[target]()
    else:
        run_command([SPHINXBUILD, "-M", target, SOURCEDIR, BUILDDIR])
