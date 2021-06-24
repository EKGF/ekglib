import argparse
import os
from itertools import chain
from pathlib import Path

import owlrl
import rdflib
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

from ..data_source import set_cli_params as data_source_set_cli_params
from ..kgiri import EKG_NS, set_kgiri_base, set_kgiri_base_replace, set_cli_params as kgiri_set_cli_params, \
                    kgiri_replace_iri_in_literal
from ..log import error, warning, log_error, log_list, log_item, log_iri
from ..main import load_rdf_file_into_graph
from ..namespace import VALIDATE, PROV, RAW, DATAOPS, DATASET

ontology_file_names = [
    'ekgf-step-story-validate.ttl'
]


def check_ontologies(ontologies_root: Path):
    if not ontologies_root.exists():
        error(f"Ontologies root directory not found: {ontologies_root}")
    for ontology_file_name in ontology_file_names:
        if not (ontologies_root / ontology_file_name).exists():
            error(f"Could not find {ontology_file_name} ontology")
    return ontologies_root


def add_story_validate_rule_namespaces(rule_graph: Graph):
    rule_graph.base = EKG_NS['KGIRI']
    rule_graph.bind("kgiri", EKG_NS['KGIRI'])
    rule_graph.bind("kggraph", EKG_NS['KGGRAPH'])
    rule_graph.namespace_manager.bind('owl', OWL)
    rule_graph.namespace_manager.bind('prov', PROV)
    rule_graph.namespace_manager.bind('raw', RAW)
    rule_graph.namespace_manager.bind('dataops', DATAOPS)
    rule_graph.namespace_manager.bind('dataset', DATASET)
    rule_graph.namespace_manager.bind('story-validate', VALIDATE)


class TransformRuleParser:
    """Checks each `rule.ttl` file in each subdirectory of `/metadata/story-validate` to
    see if it refers to `.sparql_endpoint` files that are meant to be used by the "Story Validate Step".
    Each of these `.sparql_endpoint` files is then imported (its contents) into a new version of
    the `rule.ttl` file.
    """
    g: rdflib.Graph

    def __init__(self, args, input_file_name=None, rule_file_iri: URIRef = None):

        self.args = args
        self.verbose = args.verbose
        self.story_validate_rule_file = Path(input_file_name)
        if not self.story_validate_rule_file.exists():
            error(f"{input_file_name} does not exist")
        self.rule_file_iri = rule_file_iri
        if args.data_source_code is None:
            error("No data source code specified")
        self.data_source_code = args.data_source_code
        if self.args.ontologies_root is None:
            error("Story Validate Rule Parser requires --ontologies-root to be specified")
        self.ontologies_root = check_ontologies(Path(self.args.ontologies_root))

    def check(self) -> int:
        self.g = self.read_rule_file()
        count = 0
        for story_validate_rule in self.get_rule_iris():
            if self.check_rule(story_validate_rule):
                count += 1
        if not count:
            log_error("Could not find any executable rules in {}".format(self.story_validate_rule_file))
            return 1
        self.load_ontologies()
        self.rdfs_infer()
        # log_item("# triples", len(self.g))
        self.rdfs_remove_tbox_stuff()
        # log_item("# triples", len(self.g))
        # dump_as_ttl_to_stdout(self.g)
        # exit(1)
        return 0

    def load_ontology(self, ontology_file_name: Path):
        log_item("Loading Ontology", ontology_file_name)
        load_rdf_file_into_graph(self.g, ontology_file_name)

    def load_ontologies(self):
        for ontology_file_name in ontology_file_names:
            self.load_ontology(self.ontologies_root / ontology_file_name)

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
            improved_datatypes=True,
            rdfs_closure=True,
            axiomatic_triples=False,
            datatype_axioms=False
        ).expand(self.g)

    def rdfs_remove_tbox_stuff(self):
        """
            Remove all stuff that the reasoner added that we don't need, only leave
            the rules and other abox stuff in there
        """
        self.g.remove((None, RDF.type, OWL.Ontology))
        self.g.remove((None, RDF.type, OWL.Class))
        self.g.remove((None, RDF.type, OWL.ObjectProperty))
        self.g.remove((None, RDF.type, OWL.DatatypeProperty))
        self.g.remove((None, RDF.type, OWL.FunctionalProperty))
        self.g.remove((None, RDF.type, OWL.AnnotationProperty))
        self.g.remove((None, RDF.type, OWL.DataRange))
        self.g.remove((None, RDF.type, RDFS.Class))
        self.g.remove((None, RDF.type, RDFS.Datatype))
        self.g.remove((None, RDF.type, XSD.dateTime))
        self.g.remove((None, RDF.type, XSD.boolean))
        self.g.remove((None, RDF.type, XSD.string))

        self.g.remove((None, OWL.disjointWith, XSD.dateTime))
        self.g.remove((VALIDATE, None, None))
        for subject in self.g.subjects(predicate=OWL.equivalentProperty, object=None):
            self.g.remove((subject, None, None))
        for subject in self.g.subjects(predicate=None, object=None):
            if subject.startswith(VALIDATE):
                self.g.remove((subject, None, None))

    def get_rule_iris(self):
        return chain(
            self.g.subjects(RDF.type, VALIDATE.Rule),
            self.g.subjects(RDF.type, VALIDATE.SPARQLRule)
        )

    def read_rule_file(self):
        """Parse the content of the given turtle file (which should be a Path object) and return an RDF graph"""
        rule_graph = rdflib.Graph()
        add_story_validate_rule_namespaces(rule_graph)
        load_rdf_file_into_graph(rule_graph, self.story_validate_rule_file)
        return rule_graph

    def set_key(self):
        return self.story_validate_rule_file.parent.parent.stem

    def set_iri(self):
        return EKG_NS['KGIRI'].term(f"rule-set-{self.set_key()}")

    def set_sort_key(self):
        """Produce a sort key allowing for an easy 'ORDER BY' to get all rules to be executed in order.
        This is a temporary implementation, at some point we'll have to switch over to a model where rules
        and rule-sets can specify dependencies to each other and then calculate the execution order based
        on that.
        """
        set_key = self.set_key()
        if set_key == 'generic':
            return "01-generic"
        if set_key == 'generic-last':
            return "98-generic-last"
        if set_key == 'obfuscate':
            return "99-obfuscate"
        return f"10-{set_key}"

    def key(self):
        return f"{self.set_key()}-{self.story_validate_rule_file.parent.stem}"

    def sort_key(self):
        return f"{self.set_sort_key()}-{self.story_validate_rule_file.parent.stem}"

    def create_rule_set(self):
        set_iri = self.set_iri()
        self.g.add((set_iri, RDF.type, VALIDATE.term('RuleSet')))
        self.g.add((set_iri, RDFS.label, Literal(self.set_key())))
        return set_iri

    def check_rule(self, story_validate_rule_iri) -> bool:
        log_iri("Story Validate Rule IRI", story_validate_rule_iri)
        log_item("Story Validate Rule Sort-key", self.sort_key())
        set_iri = self.create_rule_set()
        self.g.add((story_validate_rule_iri, VALIDATE.term('inSet'), set_iri))
        self.g.add((story_validate_rule_iri, VALIDATE.term('key'), Literal(self.key())))
        self.g.add((story_validate_rule_iri, VALIDATE.sortKey, Literal(self.sort_key())))
        if self.args.data_source_code:
            self.g.add((story_validate_rule_iri, DATASET.dataSourceCode, Literal(self.args.data_source_code)))
        if self.rule_file_iri:
            self.g.add((story_validate_rule_iri, VALIDATE.definedIn, self.rule_file_iri))
        for rdfs_label in self.g.objects(story_validate_rule_iri, RDFS.label):
            log_item("Story Validate Rule Title", rdfs_label)
        if self.verbose:
            print("Looking for %s" % VALIDATE.sparqlRuleFileName)
        sparql_rule_file_names = [x for x in self.g.objects(
            story_validate_rule_iri, VALIDATE.sparqlRuleFileName
        )]
        if len(sparql_rule_file_names) == 0:
            warning(f"Story validate rule {self.key()} does not have a SPARQL statement")
            return False
        if self.verbose:
            log_list('SPARQL Files', sparql_rule_file_names)
        for sparql_rule_file_name in sparql_rule_file_names:
            self.process_sparql_literal(
                story_validate_rule_iri,
                self.check_sparql_file_name(sparql_rule_file_name)
            )
        return True

    #
    # Check to see if in the same directory as the rule.ttl file we have a .sparql_endpoint file
    # with the given name. If so, return its contents as a Literal.
    #
    def check_sparql_file_name(self, sparql_file_name):
        if self.verbose:
            log_item("Checking", self.story_validate_rule_file.parent / sparql_file_name)
        sparql_file_name_full_path = self.story_validate_rule_file.parent / sparql_file_name
        if not sparql_file_name_full_path.exists():
            warning(f"Could not find {sparql_file_name_full_path}")
            return None
        log_item("Found SPARQL file", f"{self.story_validate_rule_file.parent.name}/{sparql_file_name}")
        return rdflib.Literal(sparql_file_name_full_path.read_text())

    def process_sparql_literal(self, story_validate_rule, sparql_literal):
        if not sparql_literal:
            return
        self.replace_literal_triple(
            story_validate_rule,
            VALIDATE.sparqlRuleFileName,
            VALIDATE.hasSPARQLRule,
            kgiri_replace_iri_in_literal(sparql_literal)
        )
        self.g.add((story_validate_rule, RDF.type, VALIDATE.Rule))
        self.g.add((story_validate_rule, RDF.type, VALIDATE.SPARQLRule))
        self.g.namespace_manager.bind("story-validate", VALIDATE)

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

    def dump(self, output_file) -> int:
        if not output_file:
            warning("You did not specify an output file, no output file created")
            return 1
        self.g.serialize(destination=output_file, format='ttl')
        log_item("Created", output_file)
        return 0


def runit(args, stream) -> int:
    processor = StroyValidateRuleParser(args, input_file_name=args.input)
    processor.check()
    return processor.dump(stream)


def main():
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.transform_rule_parser',
        description='Adds any referenced SPARQL file to the graph as text and writes a new Turtle file',
        epilog='Currently only supports turtle.',
        allow_abbrev=False
    )
    parser.add_argument('--verbose', '-v', help='verbose output', default=False, action='store_true')
    parser.add_argument('--input', '-i', help='The input rule.ttl file')
    parser.add_argument('--output', '-o', help='The output rule-with-sparql_endpoint.ttl file')
    parser.add_argument('--ontologies-root', help='The root directory where ontologies can be found')
    kgiri_set_cli_params(parser)
    data_source_set_cli_params(parser)
    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)
    set_kgiri_base_replace(args.kgiri_base_replace)

    if args.output is None:
        log_item("Streaming output to", "stdout")
        with os.fdopen(1, "wb", closefd=False) as stdout:
            rc = runit(args, stdout)
            stdout.flush()
    else:
        log_item("Streaming output to", args.output)
        rc = runit(args, args.output)

    return rc


if __name__ == "__main__":
    exit(main())
