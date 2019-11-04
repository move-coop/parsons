from parsons.utilities import files
from parsons.utilities import check_env
import json
import os


def setup_google_application_credentials(app_creds):
    # Detect if the app_creds string is a path or json and if it is a
    # json string, then convert it to a temporary file. Then set the
    # environmental variable.
    if app_creds:
        try:
            json.loads(app_creds)
            creds_path = files.string_to_temp_file(app_creds, suffix='.json')
        except ValueError:
            creds_path = app_creds

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path

    check_env.check('GOOGLE_APPLICATION_CREDENTIALS', app_creds)
