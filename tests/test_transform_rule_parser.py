import os
import sys
import textwrap
import ekglib


class TestTransformRuleParser:

    def test_transform_rule_parser(self, test_data_dir):
        output = 'test-transform-rule.ttl.txt'
        sys.argv = [
            'pytest',
            '--input', f'{test_data_dir}/transform/generic/00001-remove-empty-strings/rule.ttl',
            '--ontologies-root', f'{test_data_dir}/../../ontologies/',
            '--output', output,
            '--data-source-code', 'abc',
            '--kgiri-base', 'https://kg.your-company.kom'
        ]
        ekglib.transform_rule_parser.parse.main()
        with open(output) as f:
            actual = textwrap.dedent(f.read())
        os.remove(output)
        expected = textwrap.dedent('''\
            @base <https://kg.your-company.kom/id/> .
            @prefix : <https://ekgf.org/ontology/step-transform/> .
            @prefix dataset: <https://ekgf.org/ontology/dataset/> .
            @prefix kgiri: <https://kg.your-company.kom/id/> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
            
            <rule-00001-remove-emtpy-strings> a owl:Thing,
                    :Rule,
                    :SPARQLRule ;
                rdfs:label "Remove all empty strings" ;
                dataset:dataSourceCode "abc" ;
                :createsProvenance false ;
                :hasSPARQLRule """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX transform: <https://ekgf.org/ontology/step-transform/>
            
            DELETE {
            
              GRAPH ?g {
                ?s ?p ?o .
              }
            }
            WHERE {
              ?s ?p ?o .
            
              BIND('' AS ?toRemove)
            
              FILTER(isLiteral(?o))
              FILTER(STR(?o) = ?toRemove)
            }
            """ ;
                :inSet <rule-set-generic> ;
                :key "generic-00001-remove-empty-strings" ;
                :sortKey "01-generic-00001-remove-empty-strings" .
            
            <rule-set-generic> a :RuleSet ;
                rdfs:label "generic" .
                
        ''')  # noqa: W293
        print(actual)
        self.maxDiff = None
        assert expected == actual
