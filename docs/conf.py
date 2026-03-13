import subprocess
import sys
from pathlib import Path

# -- Project Setup -----------------------------------------------------------
sys.path.insert(0, str(Path("../").absolute()))

project = "Parsons"
copyright = "2025, The Movement Cooperative"
author = "The Movement Cooperative"
release = ""

# -- General Configuration ---------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_multiversion",
    "sphinxcontrib.googleanalytics",
]

master_doc = "index"
language = "en"
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "_template.rst"]
templates_path = ["_templates"]
autodoc_member_order = "bysource"

# -- HTML Output (Furo Theme) ------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
googleanalytics_id = "G-L2YB7WHTRG"

html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
        "versions.html",
    ]
}


# -- Sphinx-Multiversion Logic -----------------------------------------------
def get_git_tags() -> list[str]:
    try:
        tags = subprocess.check_output(
            ["git", "tag", "-l", "--sort=-v:refname"], encoding="utf-8", stderr=subprocess.DEVNULL
        ).splitlines()
        return [tag for tag in tags if tag.startswith("v")]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


smv_branch_whitelist = r"^stable|latest$"
DOCUMENTED_VERSIONS = get_git_tags()
smv_tag_whitelist = (
    "|".join(["^" + v + "$" for v in DOCUMENTED_VERSIONS]) if DOCUMENTED_VERSIONS else r"^$"
)
smv_remote_whitelist = None
