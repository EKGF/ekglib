import os
import sys
import textwrap

import ekglib


class TestPersonaParser:

    def test_persona_parser(self, test_data_dir):
        output_file = f'{test_data_dir}/test-persona-001.ttl.txt'
        sys.argv = [
            'pytest',
            '--input', f'{test_data_dir}/test-persona-001.ttl',
            '--output', output_file,
            '--kgiri-base', 'https://kg.your-company.kom',
        ]
        ekglib.persona_parser.parse.main()
        with open(output_file) as f:
            actual = textwrap.dedent(f.read())
        os.remove(output_file)
        expected = textwrap.dedent("""\
            @prefix persona: <https://ekgf.org/ontology/persona/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix use-case: <https://ekgf.org/ontology/use-case/> .

            <https://kg.your-company.kom/id/persona-professional> a persona:Persona ;
                rdfs:label "Professional" ;
                use-case:isInvolvedInUseCase <https://kg.your-company.kom/id/use-case-address> .
                
        """)  # noqa: W293
        print(actual)
        assert expected == actual
