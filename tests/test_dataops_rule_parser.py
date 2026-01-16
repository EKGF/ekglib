import sys

import ekg_lib


class TestDataopsRuleParser:
    def test_dataops_rule_parser(self, kgiri_base, test_data_dir):
        output = f'{test_data_dir}/dataops/test-dataops-rule.ttl.txt'
        sys.argv = [
            'pytest',
            '--input',
            f'{test_data_dir}/dataops/generic/00001-check-dataset-not-empty/rule.ttl',
            '--ontologies-root',
            f'{test_data_dir}/ontologies',
            '--output',
            output,
            '--data-source-code',
            'abc',
            '--kgiri-base',
            kgiri_base,
            '--kgiri-base-replace',
            'https://placeholder.kg',
        ]
        ekg_lib.dataops_rule_parser.parse.main()
        with open(output) as f:
            actual = f.read()

        # Check that key parts are present (exact match is too brittle due to inferred triples)
        assert f'@base <{kgiri_base}/id/>' in actual
        assert '<rule-00001-check-dataset-not-empty> a owl:Thing,' in actual
        assert ':Rule,' in actual
        assert ':SPARQLRule,' in actual
        assert ':ValidationRule' in actual
        assert 'rdfs:label "Check dataset is not empty"' in actual
        assert ':createsProvenance false' in actual
        assert ':expectedResult :BooleanResultTrue' in actual
        assert (
            'PREFIX legal-entity:  <https://ekgf.org/ontology/legal-entity/>' in actual
        )
        assert ':key "generic-00001-check-dataset-not-empty"' in actual
        assert ':sortKey "01-generic-00001-check-dataset-not-empty"' in actual
        assert ':sparqlQueryType :SPARQLAskQuery' in actual
        assert 'dataset:dataSourceCode "abc"' in actual
        assert '<rule-set-generic> a' in actual
        assert ':RuleSet' in actual
        assert 'rdfs:label "generic"' in actual
