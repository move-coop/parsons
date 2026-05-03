from typing import Any


def arg_format(arg: str) -> str:
    """
    Convert a snake_case string to a camelCase string.

    Many APIs require arguments to formatted like this: ``thisTypeConfig``.
    This is not the standard for python, so this method takes an argument
    like ``this_type_config`` and returns it like ``thisTypeConfig``.

    """
    arg_list = arg.split("_")
    arg_list = [a.capitalize() for a in arg_list]
    arg_list[0] = arg_list[0].lower()

    return "".join(arg_list)


def remove_empty_keys(dirty_dict: dict) -> dict:
    """
    Remove empty keys from a dictionary.

    Useful when passing jsons in which a null field
    will update the value to null and you don't want that.

    """
    clean_dict = {}

    for k, v in dirty_dict.items():
        if v:
            clean_dict[k] = v

    return clean_dict


def flatten_json(json: dict[str, Any] | list[dict[str, Any]] | Any) -> dict[str, Any]:
    """
    Flatten nested json to return a dict without nested values.

    Lists without nested values will be ignored, and lists of dicts
    will only return the first key value pair for each key.
    Useful for passing nested json to validation methods.

    """
    out = {}

    def flatten(x: dict[str, Any] | list[dict[str, Any]] | Any, name: str = ""):
        if type(x) is dict:
            for k, v in x.items():
                flatten(v, k)
        elif type(x) is list:
            for a in x:
                flatten(a)
        elif name != "" and name not in out:
            out[name] = x

    flatten(json)

    return out
