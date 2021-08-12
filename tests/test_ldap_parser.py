import argparse
import unittest
from tempfile import TemporaryDirectory
from unittest import mock

from ekglib.ldap_parser_to_file import main as ldap_parser_to_file
from ekglib.log import log_item


def test_export_from_ldapclient_dot_com(test_data_dir, kgiri_base, tmpdir):
    """Generic test that should always work since ldapclient.com is always up and running
    """
    output_file_name = f'{tmpdir}/test-ldap-1.nt'
    with open(output_file_name, 'xb') as output_file:
        with mock.patch(
                'argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    output=output_file,
                    ldap_naming_context=None,
                    ldap_search_filter='(objectClass=*)',
                    ldap_host="ldapclient.com",
                    ldap_port=389,
                    ldap_bind_dn=None,
                    ldap_bind_auth=None,
                    ldap_log=False,
                    ldap_timeout=60,
                    data_source_code='ldap',
                    kgiri_base=kgiri_base,
                    verbose=False
                )
        ):
            assert 0 == ldap_parser_to_file()
    print('Last 8 lines of output:')
    with open(output_file_name, 'r') as file:
        for line in (file.readlines()[-8:]):
            print(line, end='')


def test_export_from_d_trust_dot_de(test_data_dir, kgiri_base):
    """Generic test that should always work since directory.d-trust.de is always up and running.
       This is the LDAP server of the "Bundesdruckerei" (government printer/publisher), see
       https://www.bundesdruckerei.de/en/LDAP-Request
    """
    with TemporaryDirectory() as output_dir:
        output_file_name = f'{output_dir}/test-ldap-2.nt'
        with open(output_file_name, 'xb') as output_file:
            with mock.patch(
                    'argparse.ArgumentParser.parse_args',
                    return_value=argparse.Namespace(
                        output=output_file,
                        ldap_naming_context=None,
                        ldap_search_filter='(objectClass=*)',
                        ldap_host="directory.d-trust.de",
                        ldap_port=389,
                        ldap_bind_dn=None,
                        ldap_bind_auth=None,
                        ldap_log=False,
                        ldap_timeout=60,
                        data_source_code='ldap',
                        kgiri_base=kgiri_base,
                        verbose=False
                    )
            ):
                assert 0 == ldap_parser_to_file()
        print('Last 8 lines of output:')
        with open(output_file_name, 'r') as file:
            for line in (file.readlines()[-8:]):
                print(line, end='')


# def test_export_from_a_trust_dot_at(test_data_dir, kgiri_base):
#     """Generic test that should always work since ldap.a-trust.at is always up and running.
#
#        Running IBM Directory 6.3
#     """
#     with TemporaryDirectory() as output_dir:
#         output_file_name = f'{output_dir}/test-ldap-3.nt'
#         with open(output_file_name, 'xb') as output_file:
#             with mock.patch(
#                     'argparse.ArgumentParser.parse_args',
#                     return_value=argparse.Namespace(
#                         output=output_file,
#                         ldap_naming_context=None,
#                         ldap_search_filter='(objectClass=*)',
#                         ldap_host="ldap.a-trust.at",
#                         ldap_port=389,
#                         ldap_bind_dn=None,
#                         ldap_bind_auth=None,
#                         ldap_log=False,
#                         ldap_timeout=60,
#                         data_source_code='ldap',
#                         kgiri_base=kgiri_base,
#                         verbose=False
#                     )
#             ):
#                 assert 0 == ldap_parser_to_file()
#         print('Last 8 lines of output:')
#         with open(output_file_name, 'r') as file:
#             for line in (file.readlines()[-8:]):
#                 print(line, end='')
#

def test_export_from_forumsys_dot_com(test_data_dir, kgiri_base):
    """Generic test that should always work since ldap.forumsys.com is always up and running
    """
    with TemporaryDirectory() as output_dir:
        output_file_name = f'{output_dir}/test-ldap-4.nt'
        with open(output_file_name, 'xb') as output_file:
            with mock.patch(
                    'argparse.ArgumentParser.parse_args',
                    return_value=argparse.Namespace(
                        output=output_file,
                        ldap_naming_context=None,
                        ldap_search_filter='(objectClass=*)',
                        ldap_host="ldap.forumsys.com",
                        ldap_port=389,
                        ldap_bind_dn='uid=gauss,dc=example,dc=com',
                        ldap_bind_auth='password',
                        ldap_log=False,
                        ldap_timeout=60,
                        data_source_code='ldap',
                        kgiri_base=kgiri_base,
                        verbose=False
                    )
            ):
                assert 0 == ldap_parser_to_file()
        print('Last 8 lines of output:')
        with open(output_file_name, 'r') as file:
            for line in (file.readlines()[-8:]):
                print(line, end='')


def test_export_from_local_ldap_mock_server_all_naming_contexts(
        kgiri_base, ldap_naming_context, ldap_bind_dn, ldap_bind_auth, local_ldap_port, test_output_dir
):
    """This test should work if you have an LDAP mock server running at port 1389
    """
    log_item('KGIRI Base', kgiri_base)
    log_item('Bind DN', ldap_bind_dn)
    log_item('Bind Auth', ldap_bind_auth)

    output_file_name = f'{test_output_dir}/test-ldap-5.nt'
    with open(output_file_name, 'wb') as output_file:
        with mock.patch(
                'argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    output=output_file,
                    ldap_naming_context=None,
                    ldap_search_filter='(objectClass=*)',
                    ldap_host="localhost",
                    ldap_port=local_ldap_port,
                    ldap_bind_dn=ldap_bind_dn,
                    ldap_bind_auth=ldap_bind_auth,
                    ldap_log=False,
                    ldap_timeout=60,
                    data_source_code='ldap',
                    git_branch='test-branch',
                    kgiri_base=kgiri_base,
                    verbose=False
                )
        ):
            assert 0 == ldap_parser_to_file()
    print('Last 8 lines of output:')
    with open(output_file_name, 'r') as file:
        for line in (file.readlines()[-8:]):
            print(line, end='')


def test_export_from_local_ldap_mock_server_one_naming_context(
        kgiri_base, ldap_naming_context, ldap_bind_dn, ldap_bind_auth, local_ldap_port, test_output_dir
):
    """This test should work if you have an LDAP mock server running at port 1389
    """
    log_item('KGIRI Base', kgiri_base)
    log_item('Naming Context', ldap_naming_context)
    log_item('Bind DN', ldap_bind_dn)
    log_item('Bind Auth', ldap_bind_auth)

    output_file_name = f'{test_output_dir}/test-ldap-6.nt'
    with open(output_file_name, 'wb') as output_file:
        with mock.patch(
                'argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    output=output_file,
                    ldap_naming_context=ldap_naming_context,
                    ldap_search_filter='(objectClass=*)',
                    ldap_host="localhost",
                    ldap_port=local_ldap_port,
                    ldap_bind_dn=ldap_bind_dn,
                    ldap_bind_auth=ldap_bind_auth,
                    ldap_log=False,
                    ldap_timeout=60,
                    data_source_code='ldap',
                    git_branch='test-branch',
                    kgiri_base=kgiri_base,
                    verbose=False
                )
        ):
            assert 0 == ldap_parser_to_file()
    print('Last 8 lines of output:')
    with open(output_file_name, 'r') as file:
        for line in (file.readlines()[-8:]):
            print(line, end='')
