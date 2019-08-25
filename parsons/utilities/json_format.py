
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
