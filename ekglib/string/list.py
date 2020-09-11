import ast


def argv_list(param_values):
    quoted = map(lambda x: f"'{x}'", param_values)
    return ', '.join(quoted)


def test_argv_list():
    actual = argv_list(['a', 'b', 'c'])
    expected = """'a' 'b' 'c'"""
    assert actual == expected


def argv_check_list(param_values):
    if type(param_values) == list and len(param_values) == 1:
        supposed_to_be_tuple = ast.literal_eval(param_values[0])
        if type(supposed_to_be_tuple) is not tuple:
            return [supposed_to_be_tuple]
        return list(supposed_to_be_tuple)
    else:
        return param_values


def test_argv_check_list():
    actual = argv_check_list(['a', 'b', 'c'])
    expected = ['a', 'b', 'c']
    assert actual == expected
