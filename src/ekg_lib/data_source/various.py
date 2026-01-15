import os
from argparse import ArgumentParser
from typing import Any


def set_cli_params(parser: ArgumentParser) -> Any:
    ekg_data_source_code = os.getenv('EKG_DATA_SOURCE_CODE', None)
    group = parser.add_argument_group('Data Source')
    if ekg_data_source_code:
        group.add_argument(
            '--data-source-code',
            help=f'The code of the data source (default is EKG_DATA_SOURCE_CODE={ekg_data_source_code})',
            default=ekg_data_source_code,
            required=True,
        )
    else:
        group.add_argument(
            '--data-source-code',
            help='The code of the dataset (can also be set with env var EKG_DATA_SOURCE_CODE)',
            required=True,
        )
    return group
