from parsons.utilities import files
from parsons.utilities import check_env
import json
import os


def setup_google_application_credentials(app_creds, env_var_name='GOOGLE_APPLICATION_CREDENTIALS'):
    # Detect if the app_creds string is a path or json and if it is a
    # json string, then convert it to a temporary file. Then set the
    # environmental variable.
    credentials = check_env.check(env_var_name, app_creds)
    try:
        json.loads(credentials)
        creds_path = files.string_to_temp_file(credentials, suffix='.json')
    except ValueError:
        creds_path = credentials

    os.environ[env_var_name] = creds_path
