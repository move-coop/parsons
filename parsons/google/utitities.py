import typing as t
from parsons.utilities import files
from parsons.utilities import check_env
import json
import os


def setup_google_application_credentials(
    app_creds: t.Union[t.Dict, str, None],
    env_var_name: str = "GOOGLE_APPLICATION_CREDENTIALS",
) -> None:
    # Detect if app_creds is a dict, path string or json string, and if it is a
    # json string, then convert it to a temporary file. Then set the
    # environmental variable.
    credentials = check_env.check(env_var_name, app_creds)
    try:
        if type(credentials) is dict:
            credentials = json.dumps(credentials)
        if json.loads(credentials):
            creds_path = files.string_to_temp_file(credentials, suffix=".json")
    except ValueError:
        creds_path = credentials

    os.environ[env_var_name] = creds_path
