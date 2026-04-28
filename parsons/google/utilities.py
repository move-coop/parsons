import json
import os

import google
from google.oauth2 import service_account

from parsons.utilities import check_env, files


def setup_google_application_credentials(
    app_creds: dict | str | None,
    env_var_name: str = "GOOGLE_APPLICATION_CREDENTIALS",
    target_env_var_name: str | None = None,
) -> None:
    """
    Set up Google service account credentials.

    1. Detect if app_creds is a dict, path string or json string.
    2. If it is none of these, try loading it from the environment variable.
    3. If it is a dict, convert it to a json string.
    4. If it is a json string, convert it to a temporary file.
    5. Set the file path to the requested environmental variable.

    Args:
        app_creds:
            Google service account credentials.
            If ``None``, try to load from `env_var_name` environment variable.
        env_var_name:
            Name of the environment variable to load from if `app_creds` is ``None``.
            Defaults to ``GOOGLE_APPLICATION_CREDENTIALS``.
        target_env_var_name:
            Name of the environment variable to set the credentials path to.
            If ``None``, use the value of `env_var_name`.

    Raises:
        ValueError: If no credentials are provided or found in the environment.
        ValueError: If the credentials file path cannot be set to environment variable.

    """
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

    Args:
        n: int
            A positive valued integer.

    Returns:
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
    scopes: list[str] | None = None,
    subject: str | None = None,
) -> google.auth.credentials.Credentials:
    service_account_filepath = os.environ[env_var_name]

    credentials = service_account.Credentials.from_service_account_file(service_account_filepath)

    if scopes:
        credentials = credentials.with_scopes(scopes)

    if subject:
        credentials = credentials.with_subject(subject)

    return credentials
