import sys

import ekglib


class TestMaturityModelParser:

    def test_maturity_model_parser(self, test_data_dir):
        sys.argv = [
            'pytest',
            '--input', f"{test_data_dir}/maturity-model",
            '--output', test_data_dir,
            '--verbose'
        ]
        assert 0 == ekglib.maturity_model_parser.parse.main()

    def test_maturity_model_parser2(self, test_output_dir):
        sys.argv = [
            'pytest',
            '--input', "../../ekg-mm",
            '--output', f"{test_output_dir}/ekg-mm",
            '--verbose'
        ]
        assert 0 == ekglib.maturity_model_parser.parse.main()
