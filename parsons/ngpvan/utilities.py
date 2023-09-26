def action_parse(action):
    """
    Internal method to parse and validate actions, which are required for some methods
    like toggle_activist_code() and toggle_volunteer_action()
    """

    action = action.capitalize()

    if action not in ("Apply", "Remove"):

        raise ValueError("Action must be either 'Apply' or 'Remove'")

    return action


def list_to_string(string_arg):
    """
    Some methods arguments parsing of a list to a string.
    """

    if string_arg:
        return ".".join(string_arg)
    else:
        return string_arg
