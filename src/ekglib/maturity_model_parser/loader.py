from __future__ import annotations

from os import getcwd
from os.path import relpath

import owlrl
import rdflib
from io import BytesIO
from pathlib import Path
from pkg_resources import resource_stream
from rdflib import Graph

from .config import Config
from .graph import MaturityModelGraph
from ..log import error, log_item
from ..log.various import value_error, log
from ..main import load_rdf_file_into_graph
from ..main.main import load_rdf_stream_into_graph
from ..namespace import BASE_IRI_MATURITY_MODEL

ontology_file_names = ['maturity-model.ttl']


def check_ontologies(ontologies_root: Path):
    if not ontologies_root.exists():
        error(f'Ontologies root directory not found: {ontologies_root}')
    for ontology_file_name in ontology_file_names:
        if not (ontologies_root / ontology_file_name).exists():
            error(f'Could not find {ontology_file_name} ontology')
    return ontologies_root


class MaturityModelLoader:
    """Checks each turtle file in the given directory"""

    g: rdflib.Graph

    def __init__(self, config: Config):
        self.config = config

        self.g = Graph()
        self.g.base = BASE_IRI_MATURITY_MODEL

    def load(self) -> MaturityModelGraph:
        self.load_ontologies()
        self.load_model_files()
        self.rdfs_infer()
        # dump_as_ttl_to_stdout(self.g)
        log(
            'All {} triples loaded and inferred, processing them now:'.format(
                len(self.g)
            )
        )
        graph = MaturityModelGraph(self.g, self.config, self.config.verbose, 'en')
        if len(list(graph.model_nodes())) == 0:
            raise value_error('No models loaded')
        for node in graph.model_nodes():
            log_item('Loaded model', node)
        graph.rewrite_fragment_references(self.config.fragments_root)
        graph.create_sort_keys()
        return graph

    def load_ontology_from_stream(self, ontology_stream: BytesIO):
        load_rdf_stream_into_graph(self.g, ontology_stream)

    def load_ontologies(self):
        log_item('Loading', 'Ontologies')
        for ontology_file_name in ontology_file_names:
            log_item('Loading Ontology', ontology_file_name)
            stream = resource_stream('ekglib.resources.ontologies', ontology_file_name)
            self.load_ontology_from_stream(stream)

    def load_model_files(self):
        log_item('Loading', 'Model Files')
        # for turtle_file in self.root_directory.rglob("*.ttl"):
        #     log_item("Going to load", turtle_file)
        for turtle_file in self.config.model_root.rglob('*.ttl'):
            if '.venv' in str(turtle_file.resolve()):
                log_item('Skipping', turtle_file)
            else:
                self.load_model_file(Path(turtle_file))
        log_item('# asserted triples', len(self.g))

    def load_model_file(self, turtle_file: Path):
        log_item('Loading Model File', relpath(turtle_file, getcwd()))
        load_rdf_file_into_graph(self.g, turtle_file)

    def rdfs_infer(self):
        log_item('Inferring', 'Triples')
        owlrl.RDFSClosure.RDFS_Semantics(self.g, True, True, True)
        closure_class = owlrl.return_closure_class(
            owl_closure=True, rdfs_closure=True, owl_extras=True, trimming=True
        )
        owlrl.DeductiveClosure(
            closure_class,
            improved_datatypes=False,
            rdfs_closure=True,
            axiomatic_triples=False,
            datatype_axioms=False,
        ).expand(self.g)
        log_item('# triples', len(self.g))

    def add_literal_triple(self, s, p, o):
        """Add a triple to the graph with the given sparql_endpoint literal."""
        if self.config.verbose:
            print('Adding triple <{0}> - <{1}> - "{2}"'.format(s, p, o))
        self.g.add((s, p, o))

    def replace_literal_triple(self, s, p1, p2, o):
        self.g.remove((s, p1, None))
        self.add_literal_triple(s, p2, o)
