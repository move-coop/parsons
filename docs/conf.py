import subprocess

# -- Project Setup -----------------------------------------------------------
project = "Parsons"
copyright = "2019-2026, The Movement Cooperative"
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
googleanalytics_id = "G-L2YB7WHTRG"
nitpick_ignore = {
    ("py:class", "petl.util.base.Table"),  # this class is not in petl's sphinx documentation
}
nitpick_ignore_regex = {
    (r"py:.*", r"box_sdk_gen\..+"),  # box references (no linkable sphinx documentation)
    (r"py:.*", r"dbt\..+"),  # dbt references (no linkable sphinx documentation)
    (r"py:.*", r"test\..+"),  # test files are currently not linkable
}

# -- Intersphinx Mapping -----------------------------------------------------
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
        "_intersphinx/google.cloud.storage-3.10.0.objects.inv",
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

# -- Linkcheck ---------------------------------------------------------------
linkcheck_ignore_blocked_domains = [
    r"https://actionnetwork.org/mirroring/docs",
    r"https://app.periscopedata.com/app",
    r"https://boto3.amazonaws.com/v1/documentation/api/.*",
    r"https://business.facebook.com",
    r"https://cloud.google.com/python/docs/reference/bigquery/latest.*",
    r"https://console..*.google.com/.*",
    r"https://developer.salesforce.com/docs/.*",
    r"https://developers.facebook.com.*",
    r"https://docs.google.com/.*",
    r"https://hub.docker.com/repository/docker/.*",
    r"https://learn.microsoft.com/en-us/python/api/azure-storage-blob/.*",
    r"https://secure.mcommons.com/.*",
    r"https://support.civisanalytics.com/hc/en-us/articles/.*",
    r"https://www.airtable.com/create/tokens",
    r"https://www.alchemer.com.*",
    r"https://www.facebook.com/business/.*",
    r"https://www.parsonsproject.org/.*",
    r"https://www.sisense.com/blog/periscope-data-is-now-sisense-for-cloud-data-teams/",
]
linkcheck_ignore_inaccessible_anchors = [
    r"https://api.bluevote.com/docs/index#.*",
    r"https://bloomerang.com/api/rest-api/#.*",
    r"https://developer.sisense.com/guides/restApi/v1/#.*",
    r"https://docs.everyaction.com/reference/people-common-models#.*",
    r"https://docs.python.org/3/library/csv.html#.*",
    r"https://github.com/.*#.*",
    r"https://secure.actblue.com/docs/csv_api#.*",
]
linkcheck_ignore_broken_connectors = [
    r"https://.*.crowdtangle.com/.*",
    r"https://capitolcanary.com/.*",
    r"https://github.com/CrowdTangle",
]
linkcheck_ignore = (
    linkcheck_ignore_blocked_domains
    + linkcheck_ignore_inaccessible_anchors
    + linkcheck_ignore_broken_connectors
)

# -- HTML Output (Furo Theme) ------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
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


# -- Sphinx Multiversion Tag Creation ----------------------------------------
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
