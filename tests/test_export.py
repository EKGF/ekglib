import sys

import pytest

import ekglib


class TestExport:

    # TODO: Make more generic, test whether a SPARQL and S3 endpoint is available
    # @unittest.skipUnless(
    #     os.uname()[1] == 'agnosmac01.local',
    #     f"Can only run when SPARQL and S3 endpoints are available on {os.uname()[1]}"
    # )
    @pytest.mark.xfail
    def test_export(self, local_sparql_port, local_s3_port):
        sys.argv = [
            'pytest',
            '--data-source-code', 'test-data-source',
            '--s3-endpoint', f'http://localhost:{local_s3_port}',
            '--s3-bucket', 'test-bucket',
            '--aws-region', 'us - east - 1',
            '--aws-access-key-id', 'R6PV57ZD740Q76FXLSV8',
            '--aws-secret-access-key', 'NCMBGHIGM5SH0P531B80D8P53LHP5R2ZAXCGHEOF',
            '--git-branch', 'test - branch',
            '--s3-create-bucket',
            '--sparql-endpoint', f'http://localhost:{local_sparql_port}',
            '--sparql-endpoint-database', 'test',
            '--sparql-endpoint-userid', 'admin',
            '--sparql-endpoint-passwd', 'admin',
            '--kgiri-base', 'https://kg.your-company.kom',
            '--verbose'
        ]
        assert 0 == ekglib.step_export.main()
