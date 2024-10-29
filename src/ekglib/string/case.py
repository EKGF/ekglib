chars_that_do_not_belong_in_camel_case_string = ['_', ':', '-', ' ']


def is_lower_camel_case(some_string):
    if len(some_string) < 1:
        return False
    if any(e in some_string for e in chars_that_do_not_belong_in_camel_case_string):
        return False
    if some_string.islower():
        return True
    if some_string[0].isupper():
        return False
    return some_string != some_string.lower() and some_string != some_string.upper()


tests = [
    ('camel', True),
    ('_camel', False),
    ('camelCase', True),
    ('CamelCase', False),
    ('CAMELCASE', False),
    ('camelcase', True),
    ('Camelcase', False),
    ('Case', False),
    ('camel_case', False),
    ('camel-case', False),
    ('http://abc.net', False),
    ('regionLabel', True),
    ('region Label', False),
    ('Status', False),
    ('status', True),
]


def test_is_lower_camel_case():
    for test_string, expected in tests:
        assert is_lower_camel_case(test_string) is expected
