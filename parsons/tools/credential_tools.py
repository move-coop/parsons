from base64 import b64encode, b64decode
import click
import json
import os

PREFIX = "PRSNSENV"


def decode_credential(credential, save_path=None, export=True, echo=False):
    """Decode an encoded credential to a Python object.

    `Args:`
        credential: str
            An encoded credential.
        save_path: str
            The path for where to save the decoded credential.
        export: bool
            A flag for whether to export the decoded object to the environment.
            Defaults to true.
        echo: bool
            A flag for whether to print the decoded object. Defaults to False.
    `Returns:`
        dict
            The decoded object.
    """
    x = len(PREFIX)
    if credential[:x] != PREFIX:
        raise ValueError("Invalid Parsons variable.")

    decoded_str = b64decode(bytes(credential.replace(PREFIX, ""), "utf-8")).decode("utf-8")

    decoded_dict = json.loads(decoded_str)

    if save_path:
        with open(save_path, "w") as f:
            f.write(json.dumps(decoded_dict))

    if export:
        for key, val in decoded_dict.items():
            os.environ[key] = str(val)

    if echo:
        print(decoded_dict)

    return decoded_dict


def encode_from_json_str(credential):
    """Encode credential(s) from a json string.

    `Args:`
        credential: str
            The credential json string to be encoded.
    `Returns:`
        str
            The encoded credential.
    """
    data = json.loads(credential)

    json_str = json.dumps(data)
    encoded_str = PREFIX + b64encode(bytes(json_str, "utf-8")).decode("utf-8")

    return encoded_str


def encode_from_json_file(credential_file):
    """Encode credential(s) from a json file.

    `Args:`
        credential_file: str
            The path to the json file with the credential to be encoded.
    `Returns:`
        str
            The encoded credential.
    """
    with open(credential_file, "r") as f:
        data = json.load(f)

    json_str = json.dumps(data)
    encoded_str = PREFIX + b64encode(bytes(json_str, "utf-8")).decode("utf-8")

    return encoded_str


def encode_from_env(env_variables):
    """Encode credential(s) from the current environment.

    `Args:`
        env_variables: list
            The list of credentials from the environment to be encoded.
    `Returns:`
        str
            The encoded credential.
    """
    data = {}
    for var in env_variables:
        data[var] = os.environ[var]

    json_str = json.dumps(data)
    encoded_str = PREFIX + b64encode(bytes(json_str, "utf-8")).decode("utf-8")

    return encoded_str


def encode_from_dict(credential):
    """Encode credential(s) from a dictionary.

    `Args:`
        credential: dict
            The list of credentials from the environment to be encoded.
    `Returns:`
        str
            The encoded credential.
    """
    data_str = json.dumps(credential)
    encoded_str = PREFIX + b64encode(bytes(data_str, "utf-8")).decode("utf-8")

    return encoded_str


@click.command(options_metavar="[-e [-f] | -d [-xp] [-o <file>]]")
@click.argument("credential", metavar="credential")
@click.option(
    "--encode",
    "-e",
    "fn",
    flag_value="encode",
    default=True,
    help="Endcode a credential.",
)
@click.option("--decode", "-d", "fn", flag_value="decode", help="Decode an encoded credential.")
@click.option(
    "-f",
    "is_file",
    is_flag=True,
    help=("Treat <credential> as a " "path to a file. Only valid with --encode."),
)
@click.option(
    "-o",
    "save_path",
    default="",
    metavar="<file>",
    help="The path for where to save the decoded credential.",
)
@click.option(
    "-x",
    "no_export",
    is_flag=True,
    default=False,
    help=("Do not export the variable to the environment. Only " "valid with --decode."),
)
@click.option("-s", "suppress", is_flag=True, default=False, help=("Suppress " "the output."))
def main(credential, fn, is_file=False, save_path="", no_export=False, suppress=False):
    """A command line tool to encode and decode credentials.

    Use this tool when the credentials for a service are split into multiple
    parts, and you'd rather deal with them as one variable. For example, to
    connect to a Redshift database, you need 5 parts: username, password,
    database name, host name, and port. With this tool, you could encode those
    5 pieces into one string variable, which can be stored as an environment
    variable, in another credential storage system like Civis's, or whatever
    you need.

    When encoding (-e, --encode) credentials, the valid types are json string,
    path to a josn file, or a list. If passing a list, comma-separate with no
    space, the names of the environment variables to encode.

    Encoding examples:
    \b
    # Encoding a json string. Note: this assumes the output of json.dumps(str).
    `python env_tools.py -e '{"key": "val", "key2": "val2"}'`

    \b
    # Encoding a json file.
    `python env_tools.py -e -f /path/to/credentials.json`

    \b
    # Encoding a list currenct environment variables.
    `python env_tools.py -e env_var1,env_var2,env_ var3`
    """
    if fn == "encode":
        if is_file:
            enc_cred = encode_from_json_file(credential)
        else:
            try:
                cred = json.loads(credential)
                enc_cred = encode_from_dict(cred)
            except json.decoder.JSONDecodeError:
                cred = credential.split(",")
                enc_cred = encode_from_env(cred)
        if not suppress:
            print(enc_cred)
    elif fn == "decode":
        decode_credential(credential, save_path, not no_export, not suppress)
    else:
        raise ValueError("Invalid function selected. Use --help for help.")


if __name__ == "__main__":
    main()
