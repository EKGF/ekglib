import os
import sys
import textwrap

import ekglib


class TestUseCaseParser:

    def test_use_case_parser(self, kgiri_base, test_data_dir):
        output_file = f'{test_data_dir}/test-use-case-001.ttl.txt'
        sys.argv = [
            'pytest',
            '--input', f'{test_data_dir}/test-use-case-001.ttl',
            '--output', output_file,
            '--kgiri-base', kgiri_base,
            '--kgiri-base-replace', 'https://placeholder.kg',
            '--verbose'
        ]
        ekglib.use_case_parser.parse.main()

        with open(output_file) as f:
            actual = f.read()
        os.remove(output_file)
        expected = textwrap.dedent(f"""\
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix use-case: <https://ekgf.org/ontology/use-case/> .

            <{kgiri_base}/id/use-case-root> a use-case:UseCase ;
                rdfs:label "Your Top Level 'Strategic' Use Case" .
                
        """)  # noqa: W293
        print(actual)
        assert expected == actual
