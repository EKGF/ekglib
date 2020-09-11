import os
import sys
import textwrap

import ekglib


class TestConceptParser:

    def test_concepts_processor(self, test_data_dir):
        output_file = f'{test_data_dir}/test-concept-001.ttl.txt'
        sys.argv = [
            'pytest',
            '--input', f'{test_data_dir}/test-concept-001.ttl',
            '--output', output_file,
            '--kgiri-base', 'https://kg.your-company.kom'
        ]
        ekglib.concept_parser.parse.main()
        with open(output_file) as f:
            actual = textwrap.dedent(f.read())
        os.remove(output_file)
        expected = textwrap.dedent("""\
            @prefix concept: <https://ekgf.org/ontology/concept/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
            
            <https://kg.your-company.kom/id/concept-dataset-code> a concept:PropertyConcept ;
                concept:key "dataset" ;
                concept:type xsd:string .
            
            <https://kg.your-company.kom/id/concept-graph> a concept:PropertyConcept ;
                rdfs:comment "Some Comment" ;
                concept:key "graph" ;
                concept:type xsd:anyURI .
            
            <https://kg.your-company.kom/id/concept-whatever> a concept:PropertyConcept ;
                concept:key "whatever" ;
                concept:type xsd:string .
               
        """)  # noqa: W293
        print(actual)
        assert expected == actual
