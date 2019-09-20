
def arg_format(arg):
    """
    Many APIs require arguments to formatted like this 'thisTypeConfig' which is not the standard
    for python so this method takes an argument 'this_type_config' and returns it as
    'thisTypeConfig'
    """

    arg_list = arg.split('_')
    arg_list = [a.capitalize() for a in arg_list]
    arg_list[0] = arg_list[0].lower()

    return ''.join(arg_list)


def list_to_string(list_arg):

    if list_arg:
        return ','.join(list_arg)
    else:
        return None


def remove_empty_keys(dirty_dict):
    # Remove empty args in dictionary

    clean_dict = {}

    for k, v in dirty_dict.items():
        if v:
            if str and len == 0:
                break
            else:
                clean_dict[k] = v

    return clean_dict
