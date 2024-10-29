import inflection
from humps.camel import case
from pandas._libs.tslibs.timestamps import Timestamp  # noqa
from rdflib import Literal

from .case import is_lower_camel_case
from .prefix import strip_end
from ..log import error


def parse_column_name(column_name):
    if column_name == 'ID':
        return 'legacyId'
    if column_name == 'Reference Id':
        return 'referenceId'
    if isinstance(column_name, int):
        key = f'column-{column_name}'
    elif isinstance(column_name, str):
        # key = unidecode(column_name)
        key = column_name.replace('-&-', '-and-')
        key = key.replace('&', ' and ')
        # print(f"key={key} is_camel_case={is_lower_camel_case(key)}")
        if not is_lower_camel_case(key):
            key = inflection.parameterize(key)
            if not is_lower_camel_case(key):
                key = case(key)
    elif isinstance(column_name, Timestamp):
        key = f'column-{Literal(column_name).lower()}'
    else:
        error(f'Encountered unknown type {type(column_name)} for value {column_name}')
        return None
    key = key.replace('  ', ' ')
    key = key.replace('--', '-')
    key = key.replace('--', '-')
    key = strip_end(key, '-')
    return key


tests = [
    ('Country Of Formation', 'countryOfFormation'),
    ('Ho-hey-yay', 'hoHeyYay'),
    ('Ho & hey-&-yay', 'hoAndHeyAndYay'),
    (
        'Subject to special regulation (FATCA, Dodd Frank,...)',
        'subjectToSpecialRegulationFatcaDoddFrank',
    ),
    ('regionLabel', 'regionLabel'),
]


def test_parse_column_name():
    for test_string, expected in tests:
        assert parse_column_name(test_string) == expected
