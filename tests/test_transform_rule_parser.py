import os
import sys
import textwrap

import ekglib


class TestDataopsRuleParser:
    def test_dataops_rule_parser(self, kgiri_base, test_data_dir):
        output = 'test-transform-rule.ttl.txt'
        sys.argv = [
            'pytest',
            '--input',
            f'{test_data_dir}/dataops/generic/00001-remove-empty-strings/rule.ttl',
            '--ontologies-root',
            f'{test_data_dir}/ontologies/',
            '--output',
            output,
            '--data-source-code',
            'abc',
            '--kgiri-base',
            kgiri_base,
            '--kgiri-base-replace',
            'https://placeholder.kg',
        ]
        ekglib.dataops_rule_parser.parse.main()
        with open(output) as f:
            actual = f.read()
        os.remove(output)

        # Check that key parts are present (exact match is too brittle due to inferred triples)
        assert f'@base <{kgiri_base}/id/>' in actual
        assert '<rule-00001-remove-emtpy-strings> a owl:Thing,' in actual
        assert ':Rule,' in actual
        assert ':SPARQLRule,' in actual
        assert ':TransformationRule' in actual
        assert 'rdfs:label "Remove all empty strings"' in actual
        assert ':createsProvenance false' in actual
        assert 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>' in actual
        assert 'DELETE {' in actual
        assert ':key "generic-00001-remove-empty-strings"' in actual
        assert ':sortKey "01-generic-00001-remove-empty-strings"' in actual
        assert 'dataset:dataSourceCode "abc"' in actual
        assert '<rule-set-generic> a' in actual
        assert ':RuleSet' in actual
        assert 'rdfs:label "generic"' in actual
