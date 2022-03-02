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
def test_output_dir():
    if os.path.isdir('output'):
        return 'output'
    if os.path.isdir('tests/output'):
        return 'tests/output'
    return ''


@pytest.fixture
def test_ekgmm_repo_dir():
    if os.path.isdir('../../ekg-mm'):
        return '../../ekg-mm'
    pytest.skip(f"../../ekg-mm directory does not exist")
    return ''

@pytest.fixture
def test_ekgmm_docs_root():
    if os.path.isdir('../../ekg-mm/docs'):
        return '../../ekg-mm/docs'
    pytest.skip(f"../../ekg-mm/docs directory does not exist")
    return ''


def require_port(number, name):
    from ekglib.main.main import is_port_in_use
    if not is_port_in_use(number):
        pytest.skip(f"{name} mock server not running on localhost:{number}")
    return number


@pytest.fixture
def local_sparql_port():
    return require_port(5820, 'SPARQL')


@pytest.fixture
def local_ldap_port():
    return require_port(1389, 'LDAP')


@pytest.fixture
def local_s3_port():
    return require_port(9000, 'S3')


def value_for_test(directory, name, default=None):
    """Get a value from the given .test/<name> file.
    :param directory:
    :param name: the name of the single-line file that contains the value we're looking for
    :param default: a default value
    :return: the value from the given file in the .test directory
    """
    value_file = f'{directory}/.test/{name}'
    if not os.path.isfile(value_file):
        if default == None:
            raise SkipTest(f'Missing {value_file} and no default has been specified')
        dirFs = os.path.dirname(value_file)
        try:
            os.stat(dirFs)
        except:
            os.mkdir(dirFs)
        with open(value_file, 'w') as f:
            f.write("{}\n".format(default))
    with open(value_file, 'r') as f:
        return f.readline().strip('\n')


def value_list_for_test(directory, name, defaults=None):
    """Get the values from the given .test/<nane> file as a list.
    :param directory:
    :param name: the name of the file that contains the values, one per row, we're looking for
    :param defaults: a list of default values
    :return: the list with the values from the given file in the .test directory
    """
    value_file = f'{directory}/.test/{name}'
    if not os.path.isfile(value_file):
        if defaults == None:
            raise SkipTest(f'Missing {value_file} and no default has been specified')
        dirFs = os.path.dirname(value_file)
        try:
            os.stat(dirFs)
        except:
            os.mkdir(dirFs)
        with open(value_file, 'w') as f:
            for item in defaults:
                f.write("{}\n".format(item))
    with open(value_file, 'r') as f:
        return f.read().splitlines()


@pytest.fixture
def kgiri_base(test_data_dir):
    return value_for_test(test_data_dir, 'kgiri-base', 'https://kg.your-company.kom')


@pytest.fixture
def ldap_naming_context(test_data_dir):
    return value_for_test(test_data_dir, 'ldap-naming-context')


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
