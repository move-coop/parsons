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
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
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
primary_domain = "py"
autodoc_member_order = "bysource"
autosectionlabel_prefix_document = True
nitpick_ignore = {
    ("py:class", "petl.util.base.Table"),  # this class is not in petl's sphinx documentation
}
nitpick_ignore_regex = {
    (r"py:.*", r"dbt\..+"),  # dbt references (no linkable sphinx documentation)
    (r"py:.*", r"box_sdk_gen\..+"),  # box references (no linkable sphinx documentation)
    (r"py:.*", r"test\..+"),  # test files are currently not linkable
}

intersphinx_mapping_core = {
    "petl": ("https://petl.readthedocs.io/latest/", None),
    "python": ("https://docs.python.org/3", None),
    "python-dateutil": ("https://dateutil.readthedocs.io/en/stable/", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    "requests-oauthlib": ("https://requests-oauthlib.readthedocs.io/en/latest/", None),
    "simplejson": ("https://simplejson.readthedocs.io/en/latest/", None),
}
intersphinx_mapping_extras = {
    "azure-storage-blob": (
        "https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob?view=azure-python",
        "https://azuresdkdocs.z19.web.core.windows.net/python/azure-storage-blob/latest/objects.inv",
    ),
    "beautifulsoup4": ("https://beautiful-soup-4.readthedocs.io/en/latest/", None),
    "boto3": ("https://docs.aws.amazon.com/boto3/latest/", None),
    "boxsdk": ("https://box-python-sdk.readthedocs.io/en/latest/", None),
    "civis": ("https://civis-python.readthedocs.io/en/stable/", None),
    "fastavro": ("https://fastavro.readthedocs.io/en/latest/", None),
    "google-auth": ("https://googleapis.dev/python/google-auth/latest/", None),
    "google-cloud-bigquery": (
        "https://cloud.google.com/python/docs/reference/bigquery/latest/",
        "https://googleapis.dev/python/bigquery/latest/objects.inv",
    ),
    "google-cloud-storage": (
        "https://cloud.google.com/python/docs/reference/storage/latest/",
        "https://googleapis.dev/python/storage/latest/objects.inv",
    ),
    "google-cloud-storage-transfer": (
        "https://cloud.google.com/python/docs/reference/storagetransfer/latest/",
        "https://googleapis.dev/python/storagetransfer/latest/objects.inv",
    ),
    "gspread": ("https://docs.gspread.org/en/latest/", None),
    "httplib2": ("https://httplib2.readthedocs.io/en/latest/", None),
    "joblib": ("https://joblib.readthedocs.io/en/stable/", None),
    "lxml": ("https://lxml.de/apidoc/", None),
    "oauth2client": ("https://oauth2client.readthedocs.io/en/latest/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "paramiko": ("https://docs.paramiko.org/en/stable/", None),
    "protobuf": ("https://googleapis.dev/python/protobuf/latest/", None),
    "psycopg2-binary": ("https://www.psycopg.org/docs/", None),
    "pyairtable": ("https://pyairtable.readthedocs.io/en/stable/", None),
    "PyGitHub": ("https://pygithub.readthedocs.io/en/latest/", None),
    "requests-toolbelt": ("https://toolbelt.readthedocs.io/en/stable/", None),
    "rich": ("https://rich.readthedocs.io/en/stable/", None),
    "simple-salesforce": ("https://simple-salesforce.readthedocs.io/en/latest/", None),
    "slack-sdk": ("https://seratch.github.io/python-slack-sdk/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/20/", None),
    "sshtunnel": ("https://sshtunnel.readthedocs.io/en/latest/", None),
    "suds": ("https://suds.readthedocs.io/en/latest/", None),
    "twilio": ("https://www.twilio.com/docs/libraries/reference/twilio-python/9.10.4/", None),
    "urllib3": ("https://urllib3.readthedocs.io/en/stable/", None),
}
intersphinx_mapping = intersphinx_mapping_core | intersphinx_mapping_extras

# -- HTML Output (Furo Theme) ------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
googleanalytics_id = "G-L2YB7WHTRG"
html_favicon = "_static/favicon.ico"

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
