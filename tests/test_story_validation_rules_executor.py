import sys

import pytest

import ekglib


class TestStoryValidationRulesExecutor:

    def test_story_validate_rules_execute(self, kgiri_base, test_data_dir, local_sparql_port):
        sys.argv = [
            'pytest',
            '--static-datasets-root', f'{test_data_dir}/static-datasets',
            '--data-source-code', 'test',
            '--sparql-endpoint', f'http://localhost:{local_sparql_port}',
            '--sparql-endpoint-database', 'test',
            '--sparql-endpoint-userid', 'admin',
            '--sparql-endpoint-passwd', 'admin',
            '--kgiri-base', kgiri_base,
            '--rules-file', f'{test_data_dir}/story-validate/00001-check-dataset-not-empty.ttl'
        ]
        assert 0 == ekglib.story_validate_rules_execute.main()  # TODO: make more meaningful assertions here
