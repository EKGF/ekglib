import os
import sys
import textwrap
import ekglib


class TestDataopsRuleParser:

    def test_dataops_rule_parser(self, kgiri_base, test_data_dir):
        output = 'output/test-dataops-rule.ttl.txt'
        sys.argv = [
            'pytest',
            '--input', f'{test_data_dir}/dataops/generic/00001-check-dataset-not-empty/rule.ttl',
            '--ontologies-root', f'{test_data_dir}/ontologies',
            '--output', output,
            '--data-source-code', 'abc',
            '--kgiri-base', kgiri_base,
            '--kgiri-base-replace', 'https://placeholder.kg'
        ]
        ekglib.dataops_rule_parser.parse.main()
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

owl:DataRange rdfs:subClassOf rdfs:Datatype ;
    owl:equivalentClass rdfs:Datatype .

<rule-00001-check-dataset-not-empty> a owl:Thing,
        :Rule,
        :SPARQLRule,
        :ValidationRule ;
    rdfs:label "Check dataset is not empty" ;
    :createsProvenance false ;
    :expectedResult :BooleanResultTrue ;
    :hasSPARQLRule """PREFIX legal-entity:  <https://ekgf.org/ontology/legal-entity/>
ASK {{
  GRAPH ?g {{
    ?s legal-entity:madeUpPredicate ?o .
  }}
}}
""" ;
    :inSet <rule-set-generic> ;
    :key "generic-00001-check-dataset-not-empty" ;
    :sortKey "01-generic-00001-check-dataset-not-empty" ;
    :sparqlQueryType :SPARQLAskQuery ;
    dataset:dataSourceCode "abc" .

<rule-set-generic> a :RuleSet ;
    rdfs:label "generic" .
            
        ''')  # noqa: W293
        # print(actual)
        # print(expected)
        self.maxDiff = None
        assert actual == expected
