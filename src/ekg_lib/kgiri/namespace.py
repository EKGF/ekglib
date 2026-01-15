from typing import Any, Optional

from rdflib import Graph, Literal, Namespace, URIRef
from six import string_types

from ..exceptions import PrefixException

kgiri_base = None
kgiri_id_suffix = 'id/'
kgiri_graph_suffix = 'graph/'

kgiri_base_replace: Optional[URIRef] = None
kgiri_replace_enabled: bool = False

EKG_NS = {}


# NB: Using a private logger, we can't use the log library as it would introduce a cyclic dependency
def _log_item(item: str, msg: Any) -> None:
    print('\r - {:<26}: [{:}]'.format(item, msg))


def complete_ns_iri_ending(iri: Any) -> Any:
    if isinstance(iri, string_types):
        if iri.endswith('/'):
            return iri
        if iri.endswith('#'):
            return iri
        return iri + '/'
    return iri


def set_ekg_namespace(key: str, iri: str) -> None:
    global EKG_NS

    EKG_NS[key] = Namespace(complete_ns_iri_ending(iri))


def set_ekg_namespace_with_base(key: str, base: str, suffix: str) -> None:
    set_ekg_namespace(key, complete_ns_iri_ending(base) + suffix)


def set_kgiri_base(ekg_kgiri_base: Optional[str]) -> None:
    global kgiri_base

    if not ekg_kgiri_base:
        raise PrefixException('kgiri_base prefix missing')

    iri = complete_ns_iri_ending(ekg_kgiri_base)
    if kgiri_base is iri:
        return
    kgiri_base = iri

    set_ekg_namespace('KGIRI_BASE', kgiri_base)
    set_ekg_namespace_with_base('KGIRI', kgiri_base, kgiri_id_suffix)
    set_ekg_namespace_with_base('KGGRAPH', kgiri_base, kgiri_graph_suffix)

    _log_item('kgiri_base', kgiri_base)


def set_kgiri_base_replace(ekg_kgiri_base_replace: Optional[str]) -> None:
    global kgiri_base_replace
    global kgiri_replace_enabled

    if not ekg_kgiri_base_replace:
        return

    iri = complete_ns_iri_ending(ekg_kgiri_base_replace)
    if kgiri_base_replace is iri:
        return
    kgiri_base_replace = iri
    set_ekg_namespace('KGIRI_BASE_REPLACE', kgiri_base_replace)

    kgiri_replace_enabled = bool(
        kgiri_base_replace and kgiri_base_replace != kgiri_base
    )

    _log_item('kgiri_base_replace', kgiri_base_replace)
    _log_item('kgiri replacement', 'enabled' if kgiri_replace_enabled else 'diabled')


def kgiri_replace(value: Any) -> Any:
    if (
        kgiri_replace_enabled
        and isinstance(value, URIRef)
        and kgiri_base_replace is not None
        and kgiri_base is not None
    ):
        replaced = URIRef(str(value).replace(str(kgiri_base_replace), str(kgiri_base)))
        return replaced
    else:
        return value


def kgiri_replace_iri_in_graph(g: Graph) -> None:
    if not kgiri_replace_enabled:
        return
    for s, p, o in g:
        g.remove((s, p, o))
        g.add((kgiri_replace(s), kgiri_replace(p), kgiri_replace(o)))


def kgiri_replace_iri_in_literal(value: Literal) -> Literal:
    if not kgiri_replace_enabled or kgiri_base_replace is None or kgiri_base is None:
        return value
    return Literal(str(value).replace(str(kgiri_base_replace), str(kgiri_base)))
    return Literal(str(value).replace(str(kgiri_base_replace), str(kgiri_base)))
