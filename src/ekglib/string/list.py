import ast
from typing import Any


def argv_list(param_values: list[str]) -> str:
    quoted = map(lambda x: f"'{x}'", param_values)
    return ', '.join(quoted)


def test_argv_list() -> None:
    actual = argv_list(['a', 'b', 'c'])
    expected = """'a' 'b' 'c'"""
    assert actual == expected


def argv_check_list(param_values: Any) -> list[Any]:
    if type(param_values) is list and len(param_values) == 1:
        supposed_to_be_tuple = ast.literal_eval(param_values[0])
        if type(supposed_to_be_tuple) is not tuple:
            return [supposed_to_be_tuple]
        return list(supposed_to_be_tuple)
    else:
        return param_values


def test_argv_check_list() -> None:
    actual = argv_check_list(['a', 'b', 'c'])
    expected = ['a', 'b', 'c']
    assert actual == expected
