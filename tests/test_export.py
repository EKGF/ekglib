import sys

import pytest

import ekglib

from unittest import mock


class TestExport:

    def test_export(self, kgiri_base, local_sparql_port, local_s3_port):
        sys.argv = [
            'pytest',
            '--data-source-code', 'ldap',
            '--s3-endpoint', f'http://localhost:{local_s3_port}',
            '--s3-bucket', 'test-bucket',
            '--aws-region', 'us-east-1',
            '--aws-access-key-id', 'R6PV57ZD740Q76FXLSV8',
            '--aws-secret-access-key', 'NCMBGHIGM5SH0P531B80D8P53LHP5R2ZAXCGHEOF',
            '--git-branch', 'test',
            '--s3-create-bucket',
            '--sparql-endpoint', f'http://localhost:{local_sparql_port}',
            '--sparql-endpoint-database', 'staging-ldap',
            '--sparql-endpoint-userid', 'admin',
            '--sparql-endpoint-passwd', 'admin',
            '--kgiri-base', kgiri_base,
            '--verbose'
        ]
        assert 0 == ekglib.step_export.main()
