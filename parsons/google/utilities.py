import json
import os
import typing as t

import google
from google.oauth2 import service_account

from parsons.utilities import check_env, files


def setup_google_application_credentials(
    app_creds: t.Union[t.Dict, str, None],
    env_var_name: str = "GOOGLE_APPLICATION_CREDENTIALS",
    target_env_var_name: t.Optional[str] = None,
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

    if not target_env_var_name:
        target_env_var_name = env_var_name

    os.environ[target_env_var_name] = creds_path


def hexavigesimal(n: int) -> str:
    """
    Converts an integer value to the type of strings you see on spreadsheets
    (A, B,...,Z, AA, AB, ...).

    Code based on
    https://stackoverflow.com/questions/16190452/converting-from-number-to-hexavigesimal-letters

    `Args:`
        n: int
            A positive valued integer.

    `Returns:`
        str
            The hexavigeseimal representation of n
    """
    if n < 1:
        raise ValueError(f"This function only works for positive integers. Provided value {n}.")

    chars = ""
    while n != 0:
        chars = chr((n - 1) % 26 + 65) + chars  # 65 makes us start at A
        n = (n - 1) // 26
    return chars


def load_google_application_credentials(
    env_var_name: str = "GOOGLE_APPLICATION_CREDENTIALS",
    scopes: t.Optional[t.List[str]] = None,
    subject: t.Optional[str] = None,
) -> google.auth.credentials.Credentials:

    service_account_filepath = os.environ[env_var_name]

    credentials = service_account.Credentials.from_service_account_file(service_account_filepath)

    if scopes:
        credentials = credentials.with_scopes(scopes)

    if subject:
        credentials = credentials.with_subject(subject)

    return credentials
