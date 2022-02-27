import argparse
import os
from io import BytesIO
from pathlib import Path

import owlrl
import rdflib
from pkg_resources import resource_stream
from rdflib import Graph, OWL

from ekglib.log.various import value_error
from ekglib.main.main import load_rdf_stream_into_graph
from ekglib.maturity_model_parser.markdown_generator import MaturityModelMarkdownGenerator, MaturityModelGraph
from ..kgiri import EKG_NS
from ..log import error, log_item
from ..main import load_rdf_file_into_graph
from ..namespace import RULE, PROV, RAW, DATAOPS, DATASET

OWL._fail = False  # workaround for this issue: https://github.com/RDFLib/OWL-RL/issues/53

ontology_file_names = [
    'maturity-model.ttl'
]


def check_ontologies(ontologies_root: Path):
    if not ontologies_root.exists():
        error(f"Ontologies root directory not found: {ontologies_root}")
    for ontology_file_name in ontology_file_names:
        if not (ontologies_root / ontology_file_name).exists():
            error(f"Could not find {ontology_file_name} ontology")
    return ontologies_root


def add_dataops_rule_namespaces(rule_graph: Graph):
    rule_graph.base = EKG_NS['KGIRI']
    rule_graph.bind("kgiri", EKG_NS['KGIRI'])
    rule_graph.bind("kggraph", EKG_NS['KGGRAPH'])
    rule_graph.namespace_manager.bind('owl', OWL)
    rule_graph.namespace_manager.bind('prov', PROV)
    rule_graph.namespace_manager.bind('raw', RAW)
    rule_graph.namespace_manager.bind('dataops', DATAOPS)
    rule_graph.namespace_manager.bind('dataset', DATASET)
    rule_graph.namespace_manager.bind('rule', RULE)


class MaturityModelParser:
    """Checks each turtle file in the given directory
    """
    verbose: bool
    model_root: Path
    g: rdflib.Graph

    def __init__(self, verbose: bool, model_root: Path):

        self.verbose = verbose
        self.model_root = model_root

        self.g = Graph()
        self.g.base = "https://maturity-model.ekgf.org/"
        if not self.model_root.is_dir():
            raise value_error("{} is not a valid directory", self.model_root.name)

    def load(self) -> MaturityModelGraph:
        self.load_ontologies()
        self.load_model_files()
        self.rdfs_infer()
        log_item("# triples", len(self.g))
        # dump_as_ttl_to_stdout(self.g)
        return MaturityModelGraph(self.g, 'en')

    def load_ontology_from_stream(self, ontology_stream: BytesIO):
        load_rdf_stream_into_graph(self.g, ontology_stream)

    def load_ontologies(self):
        for ontology_file_name in ontology_file_names:
            log_item("Loading Ontology", ontology_file_name)
            stream = resource_stream('ekglib.resources.ontologies', ontology_file_name)
            self.load_ontology_from_stream(stream)

    def load_model_files(self):
        # for turtle_file in self.root_directory.rglob("*.ttl"):
        #     log_item("Going to load", turtle_file)
        for turtle_file in self.model_root.rglob("*.ttl"):
            self.load_model_file(Path(turtle_file))

    def load_model_file(self, turtle_file: Path):
        log_item("Loading Model File", turtle_file)
        load_rdf_file_into_graph(self.g, turtle_file)

    def rdfs_infer(self):
        owlrl.RDFSClosure.RDFS_Semantics(self.g, True, True, True)
        closure_class = owlrl.return_closure_class(
            owl_closure=True,
            rdfs_closure=True,
            owl_extras=True,
            trimming=True
        )
        owlrl.DeductiveClosure(
            closure_class,
            improved_datatypes=False,
            rdfs_closure=True,
            axiomatic_triples=False,
            datatype_axioms=False
        ).expand(self.g)

    #
    # Add a triple to the graph with the given sparql_endpoint literal.
    #
    def add_literal_triple(self, s, p, o):
        if self.verbose:
            print("Adding triple <{0}> - <{1}> - \"{2}\"".format(s, p, o))
        self.g.add((s, p, o))

    def replace_literal_triple(self, s, p1, p2, o):
        self.g.remove((s, p1, None))
        self.add_literal_triple(s, p2, o)


def mkdocs_gen_files(model_root: Path, output_root: Path):
    loader = MaturityModelParser(True, model_root)
    graph = loader.load()
    generator = MaturityModelMarkdownGenerator(graph, mkdocs=True, output_root=output_root)
    generator.generate()
    # exporter = GraphExporter(graph)
    # return exporter.export(stream)
    return 0


def runit(args) -> int:
    loader = MaturityModelParser(verbose=args.verbose, model_root=Path(args.input))
    graph = loader.load()
    generator = MaturityModelMarkdownGenerator(graph, mkdocs=False, output_root=Path(args.output))
    generator.generate()
    # exporter = GraphExporter(graph)
    # return exporter.export(stream)
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.maturity_model_parser',
        description='Generates Markdown files for all capabilities found in the given directory',
        epilog='Currently only supports turtle.',
        allow_abbrev=False
    )
    parser.add_argument('--verbose', '-v', help='verbose output', default=False, action='store_true')
    parser.add_argument('--input', '-i', help='The input directory', required=True)
    parser.add_argument('--output', '-o', help='The output directory', required=True)

    return runit(parser.parse_args())


if __name__ == "__main__":
    exit(main())
