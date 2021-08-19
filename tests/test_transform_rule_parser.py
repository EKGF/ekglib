import os
import sys
import textwrap
import ekglib


class TestTransformRuleParser:

    def test_transform_rule_parser(self, kgiri_base, test_data_dir):
        output = 'test-transform-rule.ttl.txt'
        sys.argv = [
            'pytest',
            '--input', f'{test_data_dir}/dataops/generic/00001-remove-empty-strings/rule.ttl',
            '--ontologies-root', f'{test_data_dir}/../../ontologies/',
            '--output', output,
            '--data-source-code', 'abc',
            '--kgiri-base', kgiri_base,
            '--kgiri-base-replace', 'https://placeholder.kg'
        ]
        ekglib.transform_rule_parser.parse.main()
        with open(output) as f:
            actual = textwrap.dedent(f.read())
        os.remove(output)
        expected = textwrap.dedent(f'''\
            @base <{kgiri_base}/id/> .
            @prefix : <https://ekgf.org/ontology/dataops-rule/> .
            @prefix dataset: <https://ekgf.org/ontology/dataset/> .
            @prefix kgiri: <{kgiri_base}/id/> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
            
            <rule-00001-remove-emtpy-strings> a owl:Thing,
                    :Rule,
                    :SPARQLRule,
                    :TransformationRule ;
                rdfs:label "Remove all empty strings" ;
                :createsProvenance false ;
                :hasSPARQLRule """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX rule: <https://ekgf.org/ontology/dataops-rule/>
            
            DELETE {{
            
              GRAPH ?g {{
                ?s ?p ?o .
              }}
            }}
            WHERE {{
              ?s ?p ?o .
            
              BIND('' AS ?toRemove)
            
              FILTER(isLiteral(?o))
              FILTER(STR(?o) = ?toRemove)
            }}
            """ ;
                :inSet <rule-set-generic> ;
                :key "generic-00001-remove-empty-strings" ;
                :sortKey "01-generic-00001-remove-empty-strings" ;
                dataset:dataSourceCode "abc" .
            
            <rule-set-generic> a :RuleSet ;
                rdfs:label "generic" .
                
        ''')  # noqa: W293
        print(actual)
        self.maxDiff = None
        assert actual == expected
