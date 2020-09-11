from __future__ import print_function

import sys

from rdflib import RDF, RDFS

from ..kgiri.namespace import EKG_NS  # Do a deep import
from ..string import remove_prefix


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def warning(msg):
    log("WARNING: {0}".format(msg))


def error(msg):
    """Log an error and exit the whole program immediately, use log_error for less drastic approach"""
    log_error(msg)
    exit(1)


def log_error(msg):
    eprint("\rERROR: {0}".format(msg))


def log(msg):
    print(f"\r{msg}")


def log_item(item, msg):
    log(" - {:<26}: [{:}]".format(item, msg))


def log_dump(item, object_):
    log_item(item, object_)
    log("   - {:<24}: [{:}]".format('type', type(object_)))
    if isinstance(object_, dict):
        for key, value in object_.items():
            log("   - {:<24}: [{:}]".format(key, value))


def log_rule(msg):
    log_item("*************************", f"************************************ {msg}")


def log_list(item, list_):
    log(" - {:<26}: {:}".format(item, f"{len(list_)} elements"))
    for index, list_item in enumerate(list_):
        log("   - {:<24}: [{:}]".format(index + 1, list_item))


def log_iri(item, iri):
    kgiri = EKG_NS['KGIRI']
    kggraph = EKG_NS['KGGRAPH']
    if iri.startswith(kgiri):
        log_item(item, f"kgiri:{remove_prefix(iri, kgiri)}")
    elif iri.startswith(kggraph):
        log_item(item, f"kggraph:{remove_prefix(iri, kggraph)}")
    else:
        log_item(item, iri)


def log_resource(graph, subject):
    log_iri("IRI", subject)
    for rdfs_type in graph.objects(subject, RDF.type):
        log_iri("Type", rdfs_type)
    for rdfs_label in graph.objects(subject, RDFS.label):
        log_iri("Label", rdfs_label)
