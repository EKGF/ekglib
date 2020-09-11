from rdflib import Namespace, URIRef
from six import string_types

kgiri_base = None
kgiri_id_suffix = 'id/'
kgiri_graph_suffix = 'graph/'

EKG_NS = {}


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


def set_kgiri_base(ekg_kgiri_base: URIRef):
    global kgiri_base

    kgiri_base = ekg_kgiri_base

    set_ekg_namespace('KGIRI_BASE', kgiri_base)
    set_ekg_namespace_with_base('KGIRI', kgiri_base, kgiri_id_suffix)
    set_ekg_namespace_with_base('KGGRAPH', kgiri_base, kgiri_graph_suffix)


set_kgiri_base(URIRef('https://kg.your-company.kom'))
