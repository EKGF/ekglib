import sys

import pytest

import ekglib


class TestTransformRulesCapture:

    def test_transform_rule_capture(self, kgiri_base, test_data_dir, local_s3_port):
        sys.argv = [
            'pytest',
            '--transform-root', f'{test_data_dir}/dataops',
            '--ontologies-root', '../ontologies',
            '--data-source-code', 'test-data-source',
            '--s3-endpoint', f'http://localhost:{local_s3_port}',
            '--s3-bucket', 'test-bucket',
            '--aws-region', 'us-east-1',
            '--aws-access-key-id', 'R6PV57ZD740Q76FXLSV8',  # These are just default Minio creds
            '--aws-secret-access-key', 'NCMBGHIGM5SH0P531B80D8P53LHP5R2ZAXCGHEOF',
            '--git-branch', 'test-branch',
            '--s3-create-bucket',
            '--kgiri-base', kgiri_base,
            '--kgiri-base-replace', 'https://placeholder.kg',
            '--verbose'
        ]
        assert 0 == ekglib.transform_rules_capture.main()
