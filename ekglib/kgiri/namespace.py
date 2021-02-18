from rdflib import Namespace, URIRef, Literal, Graph
from six import string_types

kgiri_base = None
kgiri_id_suffix = 'id/'
kgiri_graph_suffix = 'graph/'

kgiri_base_replace = None

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

    kgiri_base =  complete_ns_iri_ending(ekg_kgiri_base)

    set_ekg_namespace('KGIRI_BASE', kgiri_base)
    set_ekg_namespace_with_base('KGIRI', kgiri_base, kgiri_id_suffix)
    set_ekg_namespace_with_base('KGGRAPH', kgiri_base, kgiri_graph_suffix)

    # print(f"SET kgiri_base to '{kgiri_base}'")


def set_kgiri_base_replace(ekg_kgiri_base_replace: URIRef):
    global kgiri_base_replace

    kgiri_base_replace =  complete_ns_iri_ending(ekg_kgiri_base_replace)

    set_ekg_namespace('KGIRI_BASE_REPLACE', kgiri_base_replace)

    # print(f"SET kgiri_base_replace to '{kgiri_base_replace}'")

def kgiri_replace(value):
    if kgiri_base_replace == kgiri_base:
        # print(f"Replace not active: {value}")
        return value
    elif isinstance(value, URIRef):
        # print(f"kgiri_base_replace={kgiri_base_replace} kgiri_base={kgiri_base}")
        replaced = URIRef(value.replace(kgiri_base_replace, kgiri_base))
        # if replaced != value:
        #     print(f"Replacing IRI: {value} with: {replaced}")
        # else:
        #     print(f"Keeping IRI: {replaced}")
        return replaced
    else:
        # print(f"Keeping Literal: {value}")
        return value

def kgiri_replace_iri_in_graph(g: Graph):
    for s, p, o in g:
        g.remove((s, p, o))
        g.add((kgiri_replace(s), kgiri_replace(p), kgiri_replace(o)))

def kgiri_replace_iri_in_literal(value: Literal):
    return Literal(value.replace(kgiri_base_replace, kgiri_base))

set_kgiri_base(URIRef('https://kg.your-company.kom'))
set_kgiri_base_replace(URIRef('https://placeholder.kg'))
