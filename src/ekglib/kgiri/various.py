import argparse
import os
import re
import sys
import uuid
from typing import Any

import inflection
from pandas._libs.tslibs.timestamps import Timestamp  # noqa
from rdflib import Literal, URIRef

from ..string import strip_end
from .namespace import EKG_NS, set_kgiri_base, set_kgiri_base_replace


def set_cli_params(parser: argparse.ArgumentParser) -> Any:
    ekg_kgiri_base = os.getenv('EKG_KGIRI_BASE')
    if ekg_kgiri_base:
        set_kgiri_base(ekg_kgiri_base)  # should call this again after 'parse_args'
    ekg_kgiri_base_replace = os.getenv('EKG_KGIRI_BASE_REPLACE')
    if ekg_kgiri_base_replace:
        set_kgiri_base_replace(
            ekg_kgiri_base_replace
        )  # should call this again after 'parse_args'
    group = parser.add_argument_group('KGIRI')
    group.add_argument(
        '--kgiri-base',
        help='A root level URL to be used for all KGIRI types (default is env.EKG_KGIRI_BASE)',
        default=ekg_kgiri_base,
    )
    group.add_argument(
        '--kgiri-base-replace',
        help='Optionally have the KGIRI base fragment replaced with the EKG_KGIRI_BASE value, '
        'see --kgiri-base (default is env.KGIRI_BASE_REPLACE)',
        default=ekg_kgiri_base_replace,
        required=False,
    )
    return group


def kgiri_random() -> URIRef:
    return kgiri_with(f'uuid:{uuid.uuid4()}')


def kgiri_with(key: str) -> URIRef:
    return EKG_NS['KGIRI'].term(key)


special_char_map = {
    ord('ä'): 'ae',
    ord('ü'): 'ue',
    ord('ö'): 'oe',
    ord('ß'): 'ss',
    '-&-': ' and ',
    ord('&'): ' and ',
    '_': ' ',
}


def _translate_to_human_readable(key: str) -> str:
    key = re.sub(r'(?i)([a-z\d]*)', lambda m: m.group(1).lower(), key)
    return re.sub(r'^\w', lambda m: m.group(0).upper(), key)


def parse_identity_key(legacy_id: Any) -> str:
    """Try to convert a given value into a string that we can use to construct a non-obfuscated KGIRI"""
    if isinstance(legacy_id, int):
        key = f'{legacy_id}'
    elif isinstance(legacy_id, str):
        key = legacy_id.translate(special_char_map)

        key = re.sub(
            r"\b('?\w)",
            lambda match: match.group(1).capitalize(),
            inflection.dasherize(
                _translate_to_human_readable(inflection.underscore(key))
            ),
        )

        # key = inflection.titleize(key)
        key = inflection.parameterize(key, separator='-')
        # key = unidecode(legacy_id)
        # key = stringcase.spinalcase(stringcase.lowercase(key))
        # key = key.replace('"', '')
        # key = key.replace('(', '-')
        # key = key.replace(')', '-')
        # key = key.replace('/', '-')
        # key = key.replace('\\', '-')
        # key = key.replace('=', '-')
        # key = key.replace('>', '-')
        # key = key.replace('<', '-')
        # key = key.replace(':', '-')
        # key = key.replace(',', '-')
        # key = key.replace('|', '-')
        # key = key.replace('&amp;', '-and-')
        # key = key.replace('-&-', '-and-')
    elif isinstance(legacy_id, Timestamp):
        key = Literal(legacy_id).lower()
    else:
        #
        # Do not change this to a call to log.error because that cause circular dependency (TODO to fix that)s
        print(
            f'ERROR: While parsing an identity key: encountered unknown type {type(legacy_id)} for value {legacy_id}',
            file=sys.stderr,
        )
        return None
    key = key.replace('--', '-')
    key = key.replace('--', '-')
    key = strip_end(key, '-')
    return key


def parse_identity_key_with_prefix(prefix: str, legacy_id: Any) -> str:
    """See parse_identity_key()"""
    if len(prefix) > 0:
        return parse_identity_key(f'{prefix}-{legacy_id}')
    return parse_identity_key(legacy_id)
