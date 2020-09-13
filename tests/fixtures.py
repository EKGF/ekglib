import os
from unittest import SkipTest

import pytest


@pytest.fixture
def test_data_dir():
    if os.path.isdir('test_data'):
        return 'test_data'
    if os.path.isdir('tests/test_data'):
        return 'tests/test_data'
    return ''


@pytest.fixture
def local_sparql_port():
    from ekglib.main.main import is_port_in_use
    if not is_port_in_use(5820):
        pytest.skip("SPARQL mock server not running on localhost:5820")
    return 5820


@pytest.fixture
def local_ldap_port():
    from ekglib.main.main import is_port_in_use
    if not is_port_in_use(1389):
        pytest.skip("LDAP mock server not running on localhost:5820")
    return 1389


@pytest.fixture
def local_s3_port():
    from ekglib.main.main import is_port_in_use
    if not is_port_in_use(9000):
        pytest.skip("S3 mock server not running on localhost:9000")
    return 9000


def value_for_test(directory, name):
    """Get a value from the given .test/<nane> file.
    :param directory:
    :param name: the name of the single-line file that contains the value we're looking for
    :return: the value from the given file in the .test directory
    """
    value_file = f'{directory}/../../.test/{name}'
    if not os.path.isfile(value_file):
        raise SkipTest(f'Missing {value_file}')
    with open(value_file, 'r') as f:
        return f.readline().strip('\n')


def value_list_for_test(directory, name, defaults):
    """Get the values from the given .test/<nane> file as a list.
    :param directory:
    :param name: the name of the file that contains the values, one per row, we're looking for
    :param defaults: a list of default values
    :return: the list with the values from the given file in the .test directory
    """
    value_file = f'{directory}/../../.test/{name}'
    if not os.path.isfile(value_file):
        with open(value_file, 'w') as f:
            for item in defaults:
                f.write("{}\n".format(item))
    with open(value_file, 'r') as f:
        return f.read().splitlines()


@pytest.fixture
def kgiri_base(test_data_dir):
    return value_for_test(test_data_dir, 'kgiri-base')


@pytest.fixture
def ldap_search_base(test_data_dir):
    return value_for_test(test_data_dir, 'ldap-search-base')


@pytest.fixture
def ldap_bind_auth(test_data_dir):
    return value_for_test(test_data_dir, 'ldap-bind-auth')


@pytest.fixture
def ldap_bind_dn(test_data_dir):
    return value_for_test(test_data_dir, 'ldap-bind-dn')


@pytest.fixture
def xlsx_ignored_values(test_data_dir):
    return value_list_for_test(
        test_data_dir, 'xlsx-ignored-values', [
            '-Not Visible-',
            'None',
            'none',
            '--'
        ])


@pytest.fixture
def xlsx_ignored_prefixes(test_data_dir):
    return value_list_for_test(
        test_data_dir, 'xlsx-ignored-prefixes', [
            'External Auditors/',
            'Accounting Standard/',
            'World/',
            'Monitoring Internal Audit/',
            'Companies/',
            'Company/',
        ])


@pytest.fixture
def xlsx_skip_sheets(test_data_dir):
    return value_list_for_test(
        test_data_dir, 'xlsx-skip-sheets', [
            '2. How To Guide',
        ])
