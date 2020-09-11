import argparse
import os
import sys
from datetime import date

import pytest
from rdflib import RDF, term, Literal, XSD

import ekglib
from ekglib.string import argv_list
from ekglib.xlsx_parser.parser import convert_to_date, main, parse_literal


class TestXlsxProcessor:
    test_data_dir: str

    def test_parse_date(self):
        actual = convert_to_date("2019.01.10")
        expected = date(2019, 1, 10)
        assert expected == actual
        actual2 = parse_literal(actual)
        expected2 = Literal(actual, datatype=XSD.date)
        assert expected2 == actual2
        assert expected2.datatype == actual2.datatype

    def test_parse_column_name(self):
        actual = ekglib.parse_column_name('Reference ID')
        expected = 'referenceId'
        assert expected == actual

    def test_single_column_sheet_generates_string_value_triple(self, test_data_dir):
        kgiri_base = "https://kg.your-company.kom"  # Don't use fixture for this since the .xslx file uses this one
        args = argparse.Namespace(
            input=f'{test_data_dir}/single_sheet_single_column.xlsx',
            verbose=True,
            ignored_values=list(),
            ignored_prefixes=list(),
            skip_sheets=list(),
            kgiri_base=kgiri_base,
            kgiri_prefix="abc",
            data_source_code="def",
            key_column_number=1,
            strip_any_prefix=False,
            output=None
        )
        parser = ekglib.XlsxParser(args)

        rdf_string_value = ekglib.RAW.StringValue
        actual = set(parser.g.triples((
            None,
            RDF.type,
            term.URIRef(rdf_string_value)
        )))
        assert actual == {
            (term.URIRef("%s/id/data-name-popular-value-1" % kgiri_base), RDF.type, rdf_string_value),
            (term.URIRef("%s/id/data-name-boring-value-2" % kgiri_base), RDF.type, rdf_string_value),
            (term.URIRef("%s/id/data-name-random-value-3" % kgiri_base), RDF.type, rdf_string_value)
        }

    def test_xlsx_test1_dot_xlsx(self, kgiri_base, test_data_dir):
        sys.argv = [
            'pytest',
            '--input', f'{test_data_dir}/xlsx-test1.xlsx',
            '--verbose',
            '--kgiri-base', kgiri_base,
            '--kgiri-prefix', 'abc',
            '--data-source-code', 'def',
            '--key-column-number', '1'
        ]
        assert 0 == main()

    def test_xlsx_test2_dot_xlsx(self, kgiri_base, test_data_dir):
        if not os.path.isfile(f'{test_data_dir}/xlsx-test2.xlsx'):
            pytest.skip('Missing test_data/xlsx-test2.xlsx')
        sys.argv = [
            'pytest',
            '--input', f'{test_data_dir}/xlsx-test2.xlsx',
            '--kgiri-base', kgiri_base,
            '--kgiri-prefix', 'abc',
            '--data-source-code', 'def',
            '--key-column-number', 1
        ]
        assert 0 == main()

    def test_xlsx_test3_dot_xlsx(
            self, kgiri_base, test_data_dir, xlsx_ignored_values, xlsx_ignored_prefixes, xlsx_skip_sheets
    ):
        if not os.path.isfile(f'{test_data_dir}/xlsx-test3.xlsx'):
            pytest.skip('Missing test_data/xlsx-test3.xlsx')
        sys.argv = [
            'pytest',
            '--input', f'{test_data_dir}/xlsx-test3.xlsx',
            '--ignored-values', argv_list(xlsx_ignored_values),
            '--ignored-prefixes', argv_list(xlsx_ignored_prefixes),
            '--skip-sheets', argv_list(xlsx_skip_sheets),
            '--kgiri-base', kgiri_base,
            '--kgiri-prefix', 'abc',
            '--data-source-code', 'def',
            '--key-column-number', '1'
        ]
        assert 0 == main()

    def test_xlsx_test3_dot_xlsx_to_file(
            self, kgiri_base, test_data_dir, xlsx_ignored_values, xlsx_ignored_prefixes, xlsx_skip_sheets
    ):
        if not os.path.isfile(f'{test_data_dir}/xlsx-test3.xlsx'):
            pytest.skip('Missing test_data/xlsx-test3.xlsx')
        sys.argv = [
            'pytest',
            '--input', f'{test_data_dir}/xlsx-test3.xlsx',
            '--output', f'{test_data_dir}/../../xlsx-test3.ttl',
            '--ignored-values', argv_list(xlsx_ignored_values),
            '--ignored-prefixes', argv_list(xlsx_ignored_prefixes),
            '--skip-sheets', argv_list(xlsx_skip_sheets),
            '--kgiri-base', kgiri_base,
            '--kgiri-prefix', 'abc',
            '--data-source-code', 'def',
            '--key-column-number', '1'
        ]
        assert 0 == main()
