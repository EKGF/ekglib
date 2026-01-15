import getpass
import os
from argparse import ArgumentParser
from typing import Any


def dump(obj: Any) -> None:
    for attr in dir(obj):
        print('obj.%s = %r' % (attr, getattr(obj, attr)))


def set_cli_params(parser: ArgumentParser) -> None:
    ekg_sparql_endpoint = os.getenv(
        'EKG_SPARQL_ENDPOINT', 'http://host.docker.internal:5820'
    )
    ekg_data_source_code = os.getenv(
        'EKG_DATA_SOURCE_CODE', os.getenv('EKG_DATASET_CODE', None)
    )
    user = os.getenv('USER', getpass.getuser())
    if ekg_data_source_code:
        ekg_sparql_database = os.getenv(
            'EKG_SPARQL_DATABASE', f'staging-{ekg_data_source_code}-{user}'
        )
    else:
        ekg_sparql_database = os.getenv('EKG_SPARQL_DATABASE', f'staging-{user}')
    ekg_sparql_userid = os.getenv('EKG_SPARQL_USERID', None)
    ekg_sparql_passwd = os.getenv('EKG_SPARQL_PASSWD', None)

    group = parser.add_argument_group('Triple Store')

    if ekg_sparql_endpoint:
        group.add_argument(
            '--sparql-endpoint',
            help=f'The SPARQL endpoint (default is EKG_SPARQL_ENDPOINT={ekg_sparql_endpoint})',
            required=True,
            default=ekg_sparql_endpoint,
        )
    else:
        group.add_argument(
            '--sparql-endpoint',
            help='The SPARQL endpoint, can be set with env var EKG_SPARQL_ENDPOINT',
            required=True,
        )

    if ekg_sparql_database:
        group.add_argument(
            '--sparql-endpoint-database',
            '--database',
            help=f'The SPARQL database (default is EKG_SPARQL_DATABASE={ekg_sparql_database})',
            required=True,
            default=ekg_sparql_database,
        )
    else:
        group.add_argument(
            '--sparql-endpoint-database',
            '--database',
            help='The SPARQL database, can be set with env var EKG_SPARQL_DATABASE',
            required=True,
        )

    if ekg_sparql_userid:
        group.add_argument(
            '--sparql-endpoint-userid',
            help=f'The SPARQL endpoint user id (default is EKG_SPARQL_USERID={ekg_sparql_userid})',
            required=True,
            default=ekg_sparql_userid,
        )
    else:
        group.add_argument(
            '--sparql-endpoint-userid',
            help='The SPARQL endpoint user id, can be set with env var EKG_SPARQL_USERID, default is "admin"',
            required=True,
            default='admin',
        )

    if ekg_sparql_passwd:
        group.add_argument(
            '--sparql-endpoint-passwd',
            '--sparql-endpoint-password',
            help='The SPARQL endpoint password (default has been set via EKG_SPARQL_PASSWD)',
            required=True,
            default=ekg_sparql_passwd,
        )
    else:
        group.add_argument(
            '--sparql-endpoint-passwd',
            '--sparql-endpoint-password',
            help='The SPARQL endpoint password, can be set with env var EKG_SPARQL_PASSWD, default is "admin"',
            required=True,
            default='admin',
        )
