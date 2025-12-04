import argparse

from ..data_source import set_cli_params as data_source_set_cli_params
from ..kgiri import set_cli_params as kgiri_set_cli_params
from ..kgiri import set_kgiri_base

# from ..ldap_parser import LdapParser
from ..s3 import set_cli_params as s3_set_cli_params


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.ldap_parser_to_s3',
        description='Capture all information from the given LDAP endpoint and store it in S3 as an RDF "raw data" file',
        epilog='Currently only supports N-Triples output.',
        allow_abbrev=False,
    )
    parser.add_argument(
        '--verbose', '-v', help='verbose output', default=False, action='store_true'
    )
    parser.add_argument(
        '--ldap-bind-dn', help='The user that we bind with', required=True
    )
    parser.add_argument(
        '--ldap-bind-auth',
        help='The credentials of the user that we bind with',
        required=True,
    )
    parser.add_argument('--ldap-host', help='LDAP host', required=True)
    parser.add_argument('--ldap-port', help='LDAP port', type=int, required=True)
    parser.add_argument(
        '--ldap-log', help='Switch on LDAP logging', default=False, action='store_true'
    )
    parser.add_argument(
        '--ldap-naming-context',
        help='Optional, DN of the top-level entry',
        default=None,
        required=False,
    )
    parser.add_argument(
        '--ldap-search-filter',
        help='Optional, search filter',
        default='(objectClass=*)',
        required=False,
    )
    parser.add_argument(
        '--ldap-timeout', help='Specify timeout in seconds', type=int, default=60
    )
    kgiri_set_cli_params(parser)
    data_source_set_cli_params(parser)
    s3_set_cli_params(parser)

    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)

    # LdapParser(args, stream=stream)
    return 1


if __name__ == '__main__':
    exit(main())
