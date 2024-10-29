import argparse
import os
import sys
from datetime import date

import pytest
from rdflib import RDF, term, Literal, XSD

import ekglib
from ekglib.kgiri import set_kgiri_base
from ekglib.string import argv_list
from ekglib.xlsx_parser.parser import convert_to_date, main, parse_literal

from tests.fixtures import test_data_dir, kgiri_base # noqa

class TestXlsxProcessor:
    test_data_dir: str

    def test_parse_date(self):
        actual = convert_to_date('2019.01.10')
        expected = date(2019, 1, 10)
        assert expected is not None
        assert expected == actual
        actual2 = parse_literal(actual)
        assert actual2 is not None
        expected2 = Literal(actual, datatype=XSD.date)
        assert expected2 == actual2
        assert expected2.datatype == actual2.datatype

    def test_parse_column_name(self):
        actual = ekglib.parse_column_name('Reference ID')
        assert actual is not None
        expected = 'referenceId'
        assert expected == actual

    def test_single_column_sheet_generates_string_value_triple(
        self, kgiri_base, test_data_dir
    ):
        assert 'https://kg.your-company.kom' == kgiri_base
        args = argparse.Namespace(
            input=f'{test_data_dir}/single_sheet_single_column.xlsx',
            verbose=True,
            ignored_values=list(),
            ignored_prefixes=list(),
            skip_sheets=list(),
            kgiri_base=kgiri_base,
            kgiri_prefix='abc',
            data_source_code='def',
            key_column_number=1,
            strip_any_prefix=False,
            output=None,
        )
        set_kgiri_base(kgiri_base)
        parser = ekglib.XlsxParser(args)
        assert parser is not None

        rdf_string_value = ekglib.RAW.StringValue
        assert 'URIRef' == type(rdf_string_value).__name__
        assert (
            'https://ekgf.org/ontology/raw/StringValue' == rdf_string_value.toPython()
        )
        actual = set(parser.g.triples((None, RDF.type, term.URIRef(rdf_string_value))))
        assert actual == {
            (
                term.URIRef('%s/id/data-name-popular-value-1' % kgiri_base),
                RDF.type,
                rdf_string_value,
            ),
            (
                term.URIRef('%s/id/data-name-boring-value-2' % kgiri_base),
                RDF.type,
                rdf_string_value,
            ),
            (
                term.URIRef('%s/id/data-name-random-value-3' % kgiri_base),
                RDF.type,
                rdf_string_value,
            ),
        }

    def test_xlsx_test1_dot_xlsx(self, kgiri_base, test_data_dir):
        test_xlsx_file = f'{test_data_dir}/xlsx-test1.xlsx'
        if not os.path.isfile(test_xlsx_file):
            pytest.skip(f'Missing {test_xlsx_file}')
        sys.argv = [
            'pytest',
            '--input',
            test_xlsx_file,
            '--verbose',
            '--kgiri-base',
            kgiri_base,
            '--kgiri-prefix',
            'abc',
            '--data-source-code',
            'def',
            '--key-column-number',
            '1',
        ]
        assert 0 == main()

    def test_xlsx_test2_dot_xlsx(self, kgiri_base, test_data_dir):
        test_xlsx_file = f'{test_data_dir}/xlsx-test2.xlsx'
        if not os.path.isfile(test_xlsx_file):
            pytest.skip(f'Missing {test_xlsx_file}')
        sys.argv = [
            'pytest',
            '--input',
            test_xlsx_file,
            '--kgiri-base',
            kgiri_base,
            '--kgiri-prefix',
            'abc',
            '--data-source-code',
            'def',
            '--key-column-number',
            '1',
        ]
        assert 0 == main()

    def test_xlsx_test3_dot_xlsx(
        self,
        kgiri_base,
        test_data_dir,
        xlsx_ignored_values,
        xlsx_ignored_prefixes,
        xlsx_skip_sheets,
    ):
        test_xlsx_file = f'{test_data_dir}/xlsx-test3.xlsx'
        if not os.path.isfile(test_xlsx_file):
            pytest.skip(f'Missing {test_xlsx_file}')
        sys.argv = [
            'pytest',
            '--input',
            test_xlsx_file,
            '--ignored-values',
            argv_list(xlsx_ignored_values),
            '--ignored-prefixes',
            argv_list(xlsx_ignored_prefixes),
            '--skip-sheets',
            argv_list(xlsx_skip_sheets),
            '--kgiri-base',
            kgiri_base,
            '--kgiri-prefix',
            'abc',
            '--data-source-code',
            'def',
            '--key-column-number',
            '1',
        ]
        assert 0 == main()

    def test_xlsx_test3_dot_xlsx_to_file(
        self,
        kgiri_base,
        test_data_dir,
        xlsx_ignored_values,
        xlsx_ignored_prefixes,
        xlsx_skip_sheets,
    ):
        test_xlsx_file = f'{test_data_dir}/xlsx-test3.xlsx'
        if not os.path.isfile(test_xlsx_file):
            pytest.skip(f'Missing {test_xlsx_file}')
        sys.argv = [
            'pytest',
            '--input',
            test_xlsx_file,
            '--output',
            f'{test_data_dir}/../../xlsx-test3.ttl',
            '--ignored-values',
            argv_list(xlsx_ignored_values),
            '--ignored-prefixes',
            argv_list(xlsx_ignored_prefixes),
            '--skip-sheets',
            argv_list(xlsx_skip_sheets),
            '--kgiri-base',
            kgiri_base,
            '--kgiri-prefix',
            'abc',
            '--data-source-code',
            'def',
            '--key-column-number',
            '1',
        ]
        assert 0 == main()
