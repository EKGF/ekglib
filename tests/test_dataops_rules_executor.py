import sys

import pytest

import ekglib


class TestDataopsRulesExecutor:
    @pytest.mark.triple_store
    def test_dataops_rules_execute(self, kgiri_base, test_data_dir, local_sparql_port):
        sys.argv = [
            'pytest',
            '--static-datasets-root',
            f'{test_data_dir}/static-datasets',
            '--data-source-code',
            'test',
            '--rule-type',
            'https://ekgf.org/ontology/dataops-rule/ValidationRule',
            '--sparql-endpoint',
            f'http://localhost:{local_sparql_port}',
            '--sparql-endpoint-database',
            'test',
            '--sparql-endpoint-userid',
            'admin',
            '--sparql-endpoint-passwd',
            'admin',
            '--kgiri-base',
            kgiri_base,
            '--rules-file',
            f'{test_data_dir}/dataops/generic/00001-check-dataset-not-empty.ttl',
        ]
        assert (
            ekglib.dataops_rules_execute.main() == 0
        )  # TODO: make more meaningful assertions here
