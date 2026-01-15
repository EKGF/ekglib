import os  # noqa
import sys  # noqa
import pytest  # noqa
import ekg_lib  # noqa

from .fixtures import local_sparql_port, local_s3_port  # noqa
from .fixtures import local_ldap_port, ldap_naming_context, ldap_bind_dn, ldap_bind_auth  # noqa
from .fixtures import xlsx_skip_sheets, xlsx_ignored_prefixes, xlsx_ignored_values  # noqa
from .fixtures import test_data_dir, test_output_dir, kgiri_base  # noqa
from .fixtures import test_ekgmm_repo_dir, test_ekgmm_docs_root, test_ekgmm_output_dir  # noqa


def pytest_addoption(parser):
    parser.addoption(
        '--run-triple_store',
        action='store_true',
        default=False,
        help='run triple_store tests (SPARQL endpoint at http://localhost:5820)',
    )
    parser.addoption(
        '--run-object_store',
        action='store_true',
        default=False,
        help='run object_store tests (S3 endpoint at http://localhost:9000)',
    )
    parser.addoption(
        '--run-ldap', action='store_true', default=False, help='run LDAP tests'
    )


# See https://docs.pytest.org/en/stable/_modules/_pytest/hookspec.html#pytest_collection_modifyitems
def pytest_collection_modifyitems(config, items):
    if config.getoption('--run-triple_store'):
        # --run-triple_store given in cli: do not skip triple_store tests
        return
    if config.getoption('--run-object_store'):
        # --run-object_store given in cli: do not skip object_store tests
        return
    if config.getoption('--run-ldap'):
        # --run-ldap given in cli: do not skip LDAP tests
        return
    skip_triple_store = pytest.mark.skip(reason='need --run-triple_store option to run')
    skip_object_store = pytest.mark.skip(reason='need --run-object_store option to run')
    for item in items:
        print('item.keywords: ', item.keywords)
        if 'triple_store' in item.keywords:
            item.add_marker(skip_triple_store)
        if 'object_store' in item.keywords:
            item.add_marker(skip_object_store)
        if 'ldap' in item.keywords:
            item.add_marker(skip_object_store)


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'triple_store: marks test as a triple_store dependent test (SPARQL endpoint at http://localhost:5820)',
    )
    config.addinivalue_line(
        'markers',
        'object_store: marks test as an object_store dependent test (S3 endpoint at http://localhost:9000)',
    )
    config.addinivalue_line(
        'markers', 'ldap: marks test as an (external) LDAP dependent test'
    )
