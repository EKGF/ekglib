import argparse
import os
from datetime import date, datetime
from decimal import InvalidOperation
from pathlib import Path
from typing import Any, Optional, Tuple

import numpy as np
import pandas as pd
import rdflib
import stringcase
from dateutil.parser import ParserError, parse
from pandas import isna
from pandas._libs.lib import Decimal  # type: ignore[attr-defined]  # noqa
from pandas._libs.tslibs.timestamps import Timestamp  # noqa
from rdflib import PROV, RDF, RDFS, XSD, Literal, URIRef
from six import string_types

from ..data_source import set_cli_params as data_source_set_cli_params
from ..kgiri import (
    EKG_NS,
    kgiri_random,
    kgiri_with,
    parse_identity_key,
    parse_identity_key_with_prefix,
)
from ..kgiri import set_cli_params as kgiri_set_cli_params
from ..kgiri import set_kgiri_base
from ..log import error, log_item, log_list, warning
from ..main import dump_as_ttl_to_stdout
from ..namespace import DATAOPS, RAW
from ..string import (
    argv_check_list,
    common_prefix,
    parse_column_name,
    remove_prefix,
    strip_end,
)

pd.options.display.max_rows = 999  # type: ignore[attr-defined]


def parse_literal(cell: Any) -> Optional[Literal]:
    if isinstance(cell, int):
        return Literal(cell)
    elif isinstance(cell, str):
        return (
            Literal(cell) if cell else None
        )  # no need to generate triples with empty strings as object
    elif isinstance(cell, float):
        return Literal(cell)
    elif isinstance(cell, Timestamp):  # has to come before the test for type date below
        date_time: datetime = cell
        if (
            date_time.hour == 0
            and date_time.minute == 0
            and date_time.second < 2
            and date_time.microsecond < 32
        ):
            return Literal(date_time.date(), datatype=XSD.date)
        return Literal(cell, datatype=XSD.dateTime)
    elif isinstance(cell, date):
        return Literal(cell, datatype=XSD.date)
    elif isinstance(cell, datetime):
        return Literal(cell)
    elif isinstance(cell, Decimal):
        return Literal(cell)
    else:
        error(f'unknown type in parse_literal: {type(cell)}')
        return None


# noinspection PyProtectedMember
def numpy_type_2_xsd_type(value: Any) -> tuple[Any, URIRef | None]:
    from pandas.api.types import is_datetime64_any_dtype as is_datetime

    if isinstance(value, str):
        return value, XSD.string
    if isinstance(value, bool):
        return value, XSD.boolean
    elif isinstance(
        value, Timestamp
    ):  # has to come before the test for type date below
        date_time: datetime = value
        if (
            date_time.hour == 0
            and date_time.minute == 0
            and date_time.second < 2
            and date_time.microsecond < 32
        ):
            return date_time.date(), XSD.date
        return value, XSD.dateTime
    if np.issubdtype(type(value), np.integer):  # type: ignore[attr-defined]
        return value, Literal(value).datatype
    if np.issubdtype(type(value), np.floating):  # type: ignore[attr-defined]
        return value, Literal(value).datatype
    if isinstance(value, date):
        return value, XSD.date
    if is_datetime(value):
        return value, XSD.dateTime
    elif isinstance(value, Timestamp):
        return value, XSD.dateTime
    warning(f'Unknown type in numpy_type_2_xsd_type: {type(value)}')
    return (value, None)


def create_column_iri(sheet_iri: URIRef, column_name: str) -> URIRef:
    return URIRef(f'{sheet_iri}-column-{stringcase.spinalcase(column_name)}')


def strip_common_prefix_in_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    column_cells = df[column_name]
    some_prefix = os.path.commonprefix([
        str(x) for x in column_cells.astype(str).tolist()
    ])
    if not some_prefix:
        return df
    if f'{some_prefix}' == 'nan':
        return df
    if some_prefix.startswith('http://') or some_prefix.startswith('https://'):
        return df
    log_item(f"Strip prefix from '{column_name}'", some_prefix)
    #
    # Don't touch date columns
    #
    try:
        df[column_name] = pd.to_datetime(column_cells)  # type: ignore[attr-defined]
        # print(df)
        # log_item('column name', column_name)
        # exit(1)
        return df
    except ParserError:
        pass
    column_cells = column_cells.str.replace(rf'^{some_prefix}', '', regex=True)
    df[column_name] = column_cells
    return df


def strip_ignored_values(df: pd.DataFrame, ignored_values: list[str]) -> pd.DataFrame:
    for ignored_value in ignored_values:
        regex = rf'^{ignored_value}$'
        # log_item('Removing ignored value', regex)
        df = df.replace(regex, np.nan, regex=True)
    return df


def remove_ignored_prefixes(
    df: pd.DataFrame, ignored_prefixes: list[str]
) -> pd.DataFrame:
    if len(ignored_prefixes) == 0:
        return df
    for ignored_prefix in ignored_prefixes:
        regex = rf'^{ignored_prefix}'
        # log_item('Removing prefix', regex)
        df = df.replace(regex, '', regex=True)
    return df


# noinspection SpellCheckingInspection
true_values = ['Ja', 'Yes', 'Oui']
# noinspection SpellCheckingInspection
false_values = ['Nein', 'No', 'Non']

key_column_suffix = '_legacy_id'

# noinspection SpellCheckingInspection
translations = {
    'Ja': True,
    'Yes': True,
    'Oui': True,
    'No': False,
    'Nein': False,
    'Non': False,
    'None': np.nan,
}


def is_int(value: Any) -> bool:
    try:
        number = int(value)
        return bool(value == str(number))
    except (ValueError, TypeError):
        return False


def is_decimal(value: Any) -> bool:
    try:
        number = Decimal(value)
        return bool(value == str(number))
    except (InvalidOperation, TypeError):
        return False


def convert_to_date(value: Any) -> date | datetime | None:
    try:
        date_time: datetime = parse(value)
        if (
            date_time.hour == 0
            and date_time.minute == 0
            and date_time.second < 2
            and date_time.microsecond < 32
        ):
            return date_time.date()
        return date_time
    except (ParserError, OverflowError):
        return None


def convert_key_column(value: Any) -> str:
    """Add the content of key_column_suffix to every value in a key column
    to prevent NA values to be replaced with NaN
    """
    # log(f"Key column value: {value}")
    return f'{value}{key_column_suffix}'


class XlsxParser:
    def __init__(self, args: Any) -> None:
        self.verbose = args.verbose
        self.ignored_values = (
            args.ignored_values if 'ignored_values' in args else list()
        )
        self.true_values = true_values
        self.false_values = false_values
        self.ignored_prefixes = (
            args.ignored_prefixes if 'ignored_prefixes' in args else list()
        )
        # probably should drop this feature:
        self.strip_any_prefix = (
            args.strip_any_prefix if 'strip_any_prefix' in args else False
        )
        self.skip_sheets = args.skip_sheets if 'skip_sheets' in args else list()
        self.legacy_key_prefix = stringcase.spinalcase(args.kgiri_prefix)
        self.legacy_key_column_number = args.key_column_number
        self.column_names: list[str] = list()
        self.counter_rows = 0
        self.counter_cells = 0
        self.g = rdflib.Graph()
        self.add_namespaces()
        self.xlsx_file = Path(args.input)
        if not self.xlsx_file.exists():
            error(f'{self.xlsx_file} does not exist')
        key = parse_identity_key_with_prefix('xlsx-file', self.xlsx_file.stem)
        if key is None:
            raise ValueError(f'Could not parse identity key for {self.xlsx_file.stem}')
        xlsx_iri = EKG_NS['KGIRI'].term(key)
        self.g.add((xlsx_iri, RDF.type, RAW.XlsxFile))
        self.g.add((xlsx_iri, RDF.type, PROV.Entity))
        self.g.add((xlsx_iri, RAW.fileName, Literal(self.xlsx_file)))
        activity_iri = self._prov_activity_start(xlsx_iri)
        log_item('Reading XSLX file', self.xlsx_file)
        xlsx: Any = pd.ExcelFile(self.xlsx_file)  # type: ignore[attr-defined]
        log_list('Sheet Names', xlsx.sheet_names)
        log_list('Skipping Sheets', args.skip_sheets)
        for sheet_name in xlsx.sheet_names:
            self.parse_sheet(xlsx, xlsx_iri, sheet_name)
        self._prov_activity_end(activity_iri)
        log_item('Processed # sheets', len(xlsx.sheet_names))
        log_item('Processed # rows', self.counter_rows)
        log_item('Processed # cells', self.counter_cells)
        log_item('Generated # triples', len(self.g))

    def _prov_activity_start(self, xlsx_iri: URIRef) -> URIRef:
        activity_iri = kgiri_random()
        self.g.add((activity_iri, RDF.type, PROV.Activity))
        self.g.add((activity_iri, PROV.startedAtTime, Literal(datetime.utcnow())))
        self.g.add((activity_iri, PROV.used, xlsx_iri))
        return activity_iri

    def _prov_activity_end(self, activity_iri: URIRef) -> None:
        self.g.add((activity_iri, PROV.endedAtTime, Literal(datetime.utcnow())))

    def key_column_number(self, number_of_columns: int) -> int:
        return int(min(self.legacy_key_column_number, number_of_columns) - 1)

    def parse_sheet(self, xlsx: Any, xlsx_iri: URIRef, sheet_name: str) -> None:
        if sheet_name in self.skip_sheets:
            log_item('Skipping sheet', sheet_name)
            return
        log_item('Parsing Sheet', sheet_name)
        sheet_iri, sheet_name_escaped = self.parse_sheet_name(xlsx_iri, sheet_name)
        self.g.add((xlsx_iri, RAW.hasView, sheet_iri))
        #
        # First parse the sheet for its columns, don't process any rows (other then the header row)
        #
        df = xlsx.parse(sheet_name=sheet_name, index_col=None, nrows=0)
        number_of_columns = len(df.columns)
        self.parse_column_names(sheet_iri, df)
        #
        # Now we know what the number of columns in this sheet is so we can adjust the legacy_key_column_number
        #
        log_item('Number of columns', number_of_columns)
        log_item('Key Column Number', self.key_column_number(number_of_columns))
        converters = {
            self.key_column_number(number_of_columns): lambda value: convert_key_column(
                value
            )
        }
        for i in range(1, number_of_columns):
            converters[i] = lambda value, j=i: self.parse_value(value, j)  # type: ignore[misc]
        df = xlsx.parse(
            sheet_name=sheet_name,
            index_col=None,
            keep_default_na=True,
            true_values=self.true_values,
            false_values=self.false_values,
            parse_dates=True,
            na_values=self.ignored_values,
            converters=converters,
        )
        df = remove_ignored_prefixes(df, self.ignored_prefixes)
        df = self.strip_any_prefix_from_all_columns(df)
        df = strip_ignored_values(df, self.ignored_values)
        self.data_profile(sheet_iri, df)
        self.parse_rows(df, sheet_iri, sheet_name_escaped)

    def parse_value(self, value: Any, column_number: int) -> Any:  # noqa
        if not isinstance(value, string_types):
            return value
        if not value:
            return np.nan
        if value in translations:
            return translations[value]
        if value in self.ignored_values:
            return np.nan
        for prefix in self.ignored_prefixes:
            if value.startswith(prefix):
                value = value[len(prefix) :]
        if value in translations:
            return translations[value]
        if value in self.ignored_values:
            return np.nan
        if is_int(value):
            return int(value)
        if is_decimal(value):
            return Decimal(value)
        could_be_date = convert_to_date(value)
        if could_be_date:
            return could_be_date
        # log_item(f'Cell {self.column_names[column_number]}', value)
        return value

    def strip_any_prefix_from_all_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.strip_any_prefix:
            return df
        for column_name in df.columns:
            df = strip_common_prefix_in_column(df, column_name)
        return df

    def data_profile(self, sheet_iri: URIRef, df: pd.DataFrame) -> None:
        """Use pandas describe function to generate data profiling information.

        'count', 'unique', 'top', 'freq', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'
        """
        # data_profile = df.describe(include='all', datetime_is_numeric=True)
        data_profile = df.describe(include='all')  # type: ignore[operator]
        data_profile.columns = self.column_names  # type: ignore[assignment]
        # log_item('Data Profile', data_profile)
        data_profile_transposed = data_profile.transpose()
        data_profile_transposed = data_profile_transposed.set_index([
            np.arange(len(data_profile_transposed)),
            data_profile_transposed.index,
        ])
        # log_item('Data Profile Transposed', data_profile_transposed)
        # log_item('DP Columns', data_profile_transposed.columns)

        for column_number in data_profile_transposed.index:
            dpt_row = data_profile_transposed.loc[[column_number]]
            column_name = dpt_row.index[0][1]
            column_iri = create_column_iri(sheet_iri, column_name)
            # log_item('Column IRI', column_iri)
            # log_list('DPT', dpt_row.values)
            self._data_profile_metric(
                column_iri, 'count', dpt_row, 'count', XSD.integer
            )
            self._data_profile_metric(
                column_iri, 'unique', dpt_row, 'unique', XSD.integer
            )
            self._data_profile_metric(column_iri, 'top', dpt_row)
            self._data_profile_metric(column_iri, 'freq', dpt_row, 'freq', XSD.integer)
            self._data_profile_metric(column_iri, 'mean', dpt_row)
            self._data_profile_metric(column_iri, 'std', dpt_row)
            self._data_profile_metric(column_iri, 'min', dpt_row)
            self._data_profile_metric(column_iri, '25%', dpt_row, '25pct')
            self._data_profile_metric(column_iri, '50%', dpt_row, '50pct')
            self._data_profile_metric(column_iri, '75%', dpt_row, '75pct')
            self._data_profile_metric(column_iri, 'max', dpt_row)

    def _data_profile_metric(
        self,
        column_iri: URIRef,
        key: str,
        dpt_row: pd.DataFrame,
        term: str | None = None,
        datatype: Any | None = None,
    ) -> None:
        if key not in dpt_row.columns:
            return
        metric = dpt_row[key].values[0]
        if isna(metric):
            return
        # log_item(f'Metric "{key}" type', type(metric))
        # log_item(" value", metric)
        # log_item(' is integer', np.issubdtype(type(metric), np.integer))
        if datatype:
            value, value_type = metric, datatype
        else:
            value, value_type = numpy_type_2_xsd_type(metric)
        # log_item(' XSD type', f"{value} type={value_type}")
        self.g.add((
            column_iri,
            RAW.term(term if term else key),
            Literal(value, datatype=value_type),
        ))
        # if metric in np.arange(1) or key in ['count', 'unique', 'freq']:
        #     self.g.add((column_iri, RAW.term(term if term else key), Literal(metric, datatype=XSD.integer)))
        # else:
        #     self.g.add((column_iri, RAW.term(term if term else key), Literal(metric)))

    def parse_sheet_name(self, xlsx_iri: URIRef, sheet_name: str) -> Tuple[URIRef, str]:
        sheet_name_escaped = parse_identity_key_with_prefix(
            'xlsx-file-sheet', sheet_name
        )
        if sheet_name_escaped is None:
            raise ValueError(f'Could not parse identity key for sheet {sheet_name}')
        sheet_iri = EKG_NS['KGIRI'].term(sheet_name_escaped)
        self.g.add((sheet_iri, RDF.type, RAW.View))
        self.g.add((sheet_iri, RDFS.label, Literal(sheet_name)))
        self.g.add((sheet_iri, RAW.isViewIn, xlsx_iri))
        return sheet_iri, sheet_name_escaped

    def parse_column_names(self, sheet_iri: URIRef, df: pd.DataFrame) -> None:
        # log_list("Original column names", df.columns)
        #
        # Remove new lines from column names
        #
        df.rename(
            columns=lambda name: str(name).replace('\n', ' ')
            if name is not None
            else '',
            inplace=True,
        )
        #
        # Remove double spaces from column names
        #
        df.rename(
            columns=lambda name: str(name).replace('  ', ' ')
            if name is not None
            else '',
            inplace=True,
        )
        log_list('Column names', df.columns)
        #
        # Figure out if the column names all share the same prefix, of so, strip it
        #
        prefix = common_prefix(list(df.columns))
        if (
            prefix
            and not prefix.startswith('http://')
            and not prefix.startswith('https://')
        ):
            log_item('Strip Column Prefix', prefix)
            df.rename(
                columns=lambda element: remove_prefix(
                    str(element) if element is not None else '', prefix
                ),
                inplace=True,
            )
            # self.column_names = list(map(lambda element: remove_prefix(element, prefix), df.columns))
        # else:
        #     self.column_names = df.columns
        #
        # From this point onwards, we keep the slightly modified but still recognisable column names
        # in df.columns but all further modifications to the column names are stored in self.column_names
        #
        self.column_names = [
            name for name in map(parse_column_name, df.columns) if name is not None
        ]
        log_list('Column raw names', self.column_names)
        for column_index, column_name in enumerate(self.column_names):
            column_iri = create_column_iri(sheet_iri, column_name)
            self.g.add((sheet_iri, RAW.term('hasColumn'), column_iri))
            self.g.add((
                column_iri,
                RAW.term('isColumnInView'),
                sheet_iri,
            ))  # Is the inverse of the previous line
            self.g.add((column_iri, RDF.type, RAW.Column))
            self.g.add((column_iri, RDFS.label, Literal(df.columns[column_index])))
            self.g.add((column_iri, RAW.columnNumber, Literal(column_index + 1)))
            self.g.add((column_iri, RAW.localName, Literal(column_name)))
            self.g.add((column_iri, RAW.predicate, RAW.term(column_name)))

    def parse_rows(
        self, df: pd.DataFrame, sheet_iri: URIRef, sheet_name_escaped: str
    ) -> None:
        for row in df.itertuples(name=None):
            self.parse_row(sheet_iri, sheet_name_escaped, df, row)

    def parse_row(
        self,
        sheet_iri: URIRef,
        sheet_name_escaped: str,
        df: pd.DataFrame,
        row: Tuple[Any, ...],
    ) -> None:
        row_number = row[0]
        self.counter_rows += 1
        if self.verbose:
            log_item(f'Row {row_number}', row)
        resource_iri = self.construct_resource_iri(
            sheet_name_escaped, row_number, row[self.legacy_key_column_number]
        )
        if resource_iri is None:
            return
        # log_item("Resource", resource_iri)
        self.g.add((resource_iri, RDF.type, RAW.Row))
        self.g.add((resource_iri, RAW.isRowInView, sheet_iri))
        row_without_row_number = row[1:]
        for column_number, cell in enumerate(row_without_row_number):
            column_name = self.column_names[column_number]
            self.parse_cell(
                resource_iri, df, row_number, column_number, cell, column_name
            )

    def construct_resource_iri(
        self, sheet_name_escaped: str, row_number: int, legacy_id: Any
    ) -> URIRef | None:
        legacy_id = strip_end(legacy_id, key_column_suffix)
        if not legacy_id:
            return None
        # log_item("Legacy ID", legacy_id)
        key = parse_identity_key_with_prefix(sheet_name_escaped, legacy_id)
        if key is None:
            return None
        resource_iri = kgiri_with(key)
        self.g.add((resource_iri, RAW.legacyId, Literal(legacy_id)))
        self.g.add((
            resource_iri,
            RAW.legacyIdInIri,
            Literal(parse_identity_key(legacy_id)),
        ))
        self.g.add((resource_iri, RAW.viewRowNumber, Literal(row_number)))
        return resource_iri

    def parse_cell(
        self,
        resource_iri: URIRef,
        df: pd.DataFrame,
        row_number: int,
        column_number: int,
        cell: Any,
        column_name: str,
    ) -> None:  # noqa
        if isna(cell):
            return
        self.counter_cells += 1
        # if self.is_ignored_value(cell):
        #     return
        # log_item(column_name, cell)
        # log_item("type", type(cell))
        cell = self.strip_ignored_prefix(cell)
        literal = parse_literal(cell)
        if literal is None:
            return
        # log_item("Converted", literal)
        if column_number != self.legacy_key_column_number:
            self.g.add((resource_iri, RAW.term(column_name), literal))
        self.parse_cell_as_iri(cell, resource_iri, column_name)

    def parse_cell_as_iri(
        self, cell: Any, resource_iri: URIRef, column_name: str
    ) -> None:
        """Now translate every string value to an IRI for easier transformations and 'Things not Strings' concept"""
        if not isinstance(cell, string_types):
            return
        if len(cell) > 4096:  # skip the super long strings
            return
        cell_without_suffix = strip_end(cell, key_column_suffix)
        if not column_name:
            log_item('Cell', cell)
            error(f'No column name for IRI {resource_iri}')
        column_predicate = f'has{stringcase.capitalcase(column_name)}'
        key = parse_identity_key_with_prefix(column_name, cell_without_suffix)
        if key is None:
            return
        string_thing_iri = EKG_NS['KGIRI'].term(key)
        self.g.add((resource_iri, RAW.term(column_predicate), string_thing_iri))
        self.g.add((string_thing_iri, RDFS.label, Literal(cell_without_suffix)))
        self.g.add((string_thing_iri, RDF.type, RAW.StringValue))
        self.g.add((string_thing_iri, RAW.valueOf, resource_iri))
        self.g.add((string_thing_iri, RAW.forPredicate, RAW.term(column_name)))

    def strip_ignored_prefix(self, cell: Any) -> Any:
        if not isinstance(cell, str):
            return cell
        for prefix in self.ignored_prefixes:
            cell = remove_prefix(cell, prefix)
        return cell

    def is_ignored_value(self, cell: Any) -> bool:
        return cell in self.ignored_values

    def add_namespaces(self) -> None:
        self.g.base = EKG_NS['KGIRI']
        self.g.namespace_manager.bind('prov', PROV)
        self.g.namespace_manager.bind('raw', RAW)
        self.g.namespace_manager.bind('dataops', DATAOPS)

    def dump_as_ttl_to_stdout(self) -> int:
        dump_as_ttl_to_stdout(self.g)
        return 0

    def dump(self, output_file: str | Path) -> int:
        if not output_file:
            warning('You did not specify an output file, no output file created')
            return 1
        self.g.serialize(destination=output_file, encoding='UTF-8', format='ttl')
        log_item('Created', output_file)
        return 0


class _KeyColumnNumberAction(argparse.Action):
    def __call__(
        self,
        _parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        value = int(values)
        if value < 1:
            _parser.error(f'Minimum value for {option_string} is 1')
        setattr(namespace, self.dest, values)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.xlsx_parser',
        description='Capture all information from the given .xlsx file and store it as RDF "raw data"',
        epilog='Currently only supports turtle.',
        allow_abbrev=False,
    )
    parser.add_argument(
        '--input', help='The name of the input .xlsx file', required=True
    )
    parser.add_argument(
        '--output', help='The name of the output RDF file (must be .ttl)'
    )
    parser.add_argument(
        '--key-column-number',
        help='The 1-based column number containing the "legacy ID"',
        action=_KeyColumnNumberAction,
        type=int,
        default=1,
    )
    parser.add_argument(
        '--strip-any-prefix',
        help='Strip any prefix from any column if all cells in that column have the same prefix',
        default=False,
    )
    parser.add_argument(
        '--ignored-values',
        help='A list of values to ignore',
        nargs=argparse.ONE_OR_MORE,
        default=list(),
    )
    parser.add_argument(
        '--ignored-prefixes',
        help='A list of prefixes of cell values to ignore',
        nargs=argparse.ONE_OR_MORE,
        default=list(),
    )
    parser.add_argument(
        '--skip-sheets',
        help='A list of sheet names to skip',
        nargs=argparse.ONE_OR_MORE,
        default=list(),
    )
    parser.add_argument(
        '--verbose', '-v', help='verbose output', default=False, action='store_true'
    )
    kgiri_group = kgiri_set_cli_params(parser)
    kgiri_group.add_argument(
        '--kgiri-prefix',
        help='The prefix to be used to construct KGIRIs',
        default='some-type-name',
    )
    data_source_set_cli_params(parser)

    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)

    #
    # Do some optimization of the various lists we're passing through as
    # parameters, if its done via sys.argv in a test then argparse doesn't
    # do it properly.
    #
    args.ignored_values = argv_check_list(args.ignored_values)
    args.ignored_prefixes = argv_check_list(args.ignored_prefixes)
    args.skip_sheets = argv_check_list(args.skip_sheets)

    if 'ignored_values' in args and len(args.ignored_values) > 0:
        log_list('Ignored Values', args.ignored_values)

    if 'ignored_prefixes' in args and len(args.ignored_prefixes) > 0:
        log_list('Ignored Prefixes', args.ignored_prefixes)

    if 'skip_sheets' in args and len(args.skip_sheets) > 0:
        log_list('Skip Sheets', args.skip_sheets)

    if 'key_column_number' in args:
        log_item('Key Column Number', args.key_column_number)

    xlsx_parser = XlsxParser(args)
    return (
        xlsx_parser.dump(args.output)
        if args.output
        else xlsx_parser.dump_as_ttl_to_stdout()
    )


if __name__ == '__main__':
    exit(main())
