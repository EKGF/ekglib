import sys

import pytest

import ekglib


class TestTransformRulesExecutor:

    def test_transform_rule_executor(self, kgiri_base, test_data_dir, local_sparql_port):
        sys.argv = [
            'pytest',
            '--static-datasets-root', f'{test_data_dir}/static-datasets',
            '--data-source-code', 'test',
            '--sparql-endpoint', f'http://localhost:{local_sparql_port}',
            '--sparql-endpoint-database', 'test',
            '--sparql-endpoint-userid', 'admin',
            '--sparql-endpoint-passwd', 'admin',
            '--kgiri-base', kgiri_base
        ]
        assert 0 == ekglib.transform_rules_execute.main()  # TODO: make more meaningful assertions here
