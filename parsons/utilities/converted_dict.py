class converted_dict(object):
    # For when you need to apply a consistent transformation to all the keys
    # in a dictionary, including the keys of embedded dictionaries within.
    # The conversion_function must take the string as argument

    def __init__(self, dct, conversion_function, kwargs=None):
        if kwargs is None:
            kwargs = {}
        self.result = self.key_converter(dct, conversion_function, kwargs)

    def key_converter(self, dct, conversion_function, kwargs):
        final_dct = {}
        for k, v in dct.items():
            final_val = v
            if isinstance(v, dict):
                final_val = self.key_converter(v, conversion_function, kwargs)
            elif isinstance(v, list):
                final_val = self.list_loop(v, conversion_function, kwargs)
            final_key = conversion_function(k, *kwargs)
            final_dct[final_key] = final_val
        return final_dct

    def list_loop(self, lst, conversion_function, kwargs):
        dicts = [x for x in lst if isinstance(x, dict)]
        lists = [x for x in lst if isinstance(x, list)]
        final_lst = [x for x in lst if x not in dicts and x not in lists]
        for d in dicts:
            final_lst.append(self.key_converter(d, conversion_function, kwargs))
        for l in lists:
            final_lst.append(self.list_loop(l, conversion_function, kwargs))
        return final_lst
