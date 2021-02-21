from rdflib import Namespace, URIRef, Literal, Graph
from six import string_types
from typing import Optional

from ..exceptions import PrefixException

kgiri_base = None
kgiri_id_suffix = 'id/'
kgiri_graph_suffix = 'graph/'

kgiri_base_replace: Optional[URIRef] = None
kgiri_replace_enabled: bool = False

EKG_NS = {}

# NB: Using a private logger, we can't use the log library as it would introduce a cyclic dependency
def _log(msg):
    print(f"\r{msg}")

def complete_ns_iri_ending(iri):
    if isinstance(iri, string_types):
        if iri.endswith('/'):
            return iri
        if iri.endswith('#'):
            return iri
        return iri + '/'
    return iri


def set_ekg_namespace(key: str, iri: str):
    global EKG_NS

    EKG_NS[key] = Namespace(complete_ns_iri_ending(iri))


def set_ekg_namespace_with_base(key: str, base: str, suffix: str):
    set_ekg_namespace(key, complete_ns_iri_ending(base) + suffix)


def set_kgiri_base(ekg_kgiri_base: Optional[str]):
    global kgiri_base

    if not ekg_kgiri_base:
        raise(PrefixException("kgiri_base prefix missing"))

    iri = complete_ns_iri_ending(ekg_kgiri_base)
    if kgiri_base is iri:
        return
    kgiri_base = iri

    set_ekg_namespace('KGIRI_BASE', kgiri_base)
    set_ekg_namespace_with_base('KGIRI', kgiri_base, kgiri_id_suffix)
    set_ekg_namespace_with_base('KGGRAPH', kgiri_base, kgiri_graph_suffix)

    _log(f"SET kgiri_base to '{kgiri_base}'")


def set_kgiri_base_replace(ekg_kgiri_base_replace: Optional[str]):
    global kgiri_base_replace
    global kgiri_replace_enabled

    if not ekg_kgiri_base_replace:
        return

    iri = complete_ns_iri_ending(ekg_kgiri_base_replace)
    if kgiri_base_replace is iri:
        return
    kgiri_base_replace = iri

    _log(f"SET kgiri_base_replace to '{kgiri_base_replace}'")

    set_ekg_namespace('KGIRI_BASE_REPLACE', kgiri_base_replace)

    kgiri_replace_enabled = (kgiri_base_replace and kgiri_base_replace != kgiri_base)
    if kgiri_replace_enabled:
        _log(f"Replacing base IRI prefixes: {kgiri_base_replace} with: {kgiri_base}")
    else:
        _log(f"Keeping base IRI prefixes: {kgiri_base}. IRI replacement is not active.")


def kgiri_replace(value):
    if kgiri_replace_enabled and isinstance(value, URIRef):
        replaced = URIRef(value.replace(kgiri_base_replace, kgiri_base))
        return replaced
    else:
        return value

def kgiri_replace_iri_in_graph(g: Graph):
    if not kgiri_replace_enabled:
        return
    for s, p, o in g:
        g.remove((s, p, o))
        g.add((kgiri_replace(s), kgiri_replace(p), kgiri_replace(o)))

def kgiri_replace_iri_in_literal(value: Literal):
    if not kgiri_replace_enabled:
        return value
    return Literal(value.replace(kgiri_base_replace, kgiri_base))
