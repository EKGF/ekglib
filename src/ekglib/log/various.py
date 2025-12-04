from __future__ import print_function

import sys
from typing import Any

from rdflib import RDF, RDFS, Graph

from ..kgiri.namespace import EKG_NS  # Do a deep import
from ..string import remove_prefix


def eprint(*args: Any, **kwargs: Any) -> None:
    print(*args, file=sys.stderr, **kwargs)


def warning(msg: str) -> None:
    log('WARNING: {0}'.format(msg))


def error(msg: str) -> None:
    """Log an error and exit the whole program immediately, use log_error for less drastic approach"""
    log_error(msg)
    exit(1)


def log_error(msg: str) -> None:
    eprint('\rERROR: {0}'.format(msg))


def value_error(*args: Any) -> ValueError:
    """Log an error and return a ValueError exception that you can raise yourself"""
    line = args[0].format(*args[1:])
    eprint(line)
    return ValueError(line)


def log(msg: str) -> None:
    print(f'\r{msg}')


def log_item(item: str, msg: Any) -> None:
    log(' - {:<26}: [{:}]'.format(item, msg))


def log_exception(e: Exception | None = None) -> None:
    if e:
        log_item('Exception', f'{repr(e)}: {e.args}')
    else:
        log_list('Exception', sys.exc_info())


def log_dump(item: str, object_: Any) -> None:
    log_item(item, object_)
    log('   - {:<24}: [{:}]'.format('type', type(object_)))
    if isinstance(object_, dict):
        for key, value in object_.items():
            log('   - {:<24}: [{:}]'.format(key, value))


def log_rule(msg: str) -> None:
    log_item('*************************', f'************************************ {msg}')


def log_list(item: str, list_: Any) -> None:
    log(' - {:<26}: {:}'.format(item, f'{len(list_)} elements'))
    for index, list_item in enumerate(list_):
        log('   - {:<24}: [{:}]'.format(index + 1, list_item))


def log_iri(item: str, iri: str) -> None:
    kgiri = EKG_NS['KGIRI']
    kggraph = EKG_NS['KGGRAPH']
    if iri.startswith(kgiri):
        log_item(item, f'kgiri:{remove_prefix(iri, kgiri)}')
    elif iri.startswith(kggraph):
        log_item(item, f'kggraph:{remove_prefix(iri, kggraph)}')
    else:
        log_item(item, iri)


def log_resource(graph: Graph, subject: Any) -> None:
    log_iri('IRI', str(subject))
    for rdfs_type in graph.objects(subject, RDF.type):
        log_iri('Type', str(rdfs_type))
    for rdfs_label in graph.objects(subject, RDFS.label):
        log_iri('Label', str(rdfs_label))
