from .namespace import (
    EKG_NS as EKG_NS,
    set_ekg_namespace as set_ekg_namespace,
    set_kgiri_base as set_kgiri_base,
    set_kgiri_base_replace as set_kgiri_base_replace,
    complete_ns_iri_ending as complete_ns_iri_ending,
    kgiri_replace as kgiri_replace,
    kgiri_replace_iri_in_graph as kgiri_replace_iri_in_graph,
    kgiri_replace_iri_in_literal as kgiri_replace_iri_in_literal,
)  # noqa: F401
from .various import (
    kgiri_with as kgiri_with,
    kgiri_random as kgiri_random,
    set_cli_params as set_cli_params,
    parse_identity_key as parse_identity_key,
    parse_identity_key_with_prefix as parse_identity_key_with_prefix,
)  # noqa: F401
