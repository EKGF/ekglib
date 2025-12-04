import argparse
from pathlib import Path

import rdflib
from rdflib.namespace import RDF, RDFS

from ..kgiri import (
    kgiri_replace_iri_in_graph,
    kgiri_replace_iri_in_literal,
    set_kgiri_base,
    set_kgiri_base_replace,
)
from ..kgiri import set_cli_params as kgiri_set_cli_params
from ..log import log_error, log_item, warning
from ..namespace import EKGPSS, USERSTORY


class UserStoryParser:
    """gets the IRI of the user story from a given user-story.ttl file"""

    def __init__(self, input_file_name: str, verbose: bool) -> None:
        self.verbose = verbose
        self.userStoryFile = Path(input_file_name)
        self.g = rdflib.Graph()

    def check(self) -> int:
        if not self.userStoryFile.exists():
            log_error(f'%s does not exist: {self.userStoryFile}')
            return 1
        with self.userStoryFile.open('r') as file:
            self.g.parse(source=file, format='turtle')
            kgiri_replace_iri_in_graph(self.g)
        log_item('Number of triples', len(self.g))
        for user_story in self.g.subjects(RDF.type, USERSTORY.UserStory):
            log_item('User Story', user_story)
            assert isinstance(user_story, rdflib.URIRef)
            self.check_story_label(user_story)
            self.check_story_base_name(user_story)
            self.check_story_sparql(user_story)
        return 0

    def check_story_label(self, user_story: rdflib.URIRef) -> None:
        count = 0
        for rdfsLabel in self.g.objects(user_story, RDFS.label):
            count += 1
            log_item('User Story Title', rdfsLabel)
        if count == 0:
            warning('User Story does not have an rdfs:label')
        if count > 1:
            warning('User Story has multiple rdfs:labels')

    def check_story_base_name(self, user_story: rdflib.URIRef) -> None:
        self.g.remove((user_story, USERSTORY.baseName, None))
        self.add_literal_triple(
            user_story, USERSTORY.baseName, self.userStoryFile.parent.stem
        )

    def check_story_sparql(self, user_story: rdflib.URIRef) -> None:
        if self.verbose:
            log_item('Looking for triple', EKGPSS.sparqlStatementFileName)
        count = 0
        for sparqlStatementFileName in self.g.objects(
            user_story, EKGPSS.sparqlStatementFileName
        ):
            count += 1
            self.process_sparql_literal(
                user_story, self.check_sparql_file_name(str(sparqlStatementFileName))
            )
        if count == 0:
            warning(f'User Story does not have an {EKGPSS.sparqlStatementFileName}')
        if count > 1:
            warning(f'User Story has multiple {EKGPSS.sparqlStatementFileName}')

    #
    # Check to see if in the same directory as the user-story.ttl file we have a .sparql file
    # with the given name. If so, return its contents as a Literal.
    #
    def check_sparql_file_name(
        self, sparql_file_name: str
    ) -> rdflib.term.Literal | None:
        log_item('Checking', self.userStoryFile.parent / sparql_file_name)
        sparql_file_name_full_path = self.userStoryFile.parent / sparql_file_name
        if not sparql_file_name_full_path.exists():
            warning('Could not find %s' % sparql_file_name_full_path)
            return None
        log_item('Found SPARQL file', sparql_file_name_full_path)
        return rdflib.Literal(sparql_file_name_full_path.read_text().strip())

    def process_sparql_literal(
        self, user_story: rdflib.term.URIRef, sparql_literal: rdflib.term.Literal | None
    ) -> None:
        if not sparql_literal:
            return
        self.replace_literal_triple(
            user_story,
            EKGPSS.sparqlStatementFileName,
            EKGPSS.hasNamedSparqlStatement,
            kgiri_replace_iri_in_literal(sparql_literal),
        )
        self.g.add((user_story, RDF.type, EKGPSS.SPARQLStatement))
        self.g.namespace_manager.bind('ekgp-uss', EKGPSS)

    #
    # Add a triple to the graph with the given sparql literal.
    #
    def add_literal_triple(
        self, s: rdflib.term.URIRef, p: rdflib.term.URIRef, o: str
    ) -> None:
        self.g.add((s, p, rdflib.term.Literal(o)))

    def replace_literal_triple(
        self,
        s: rdflib.term.URIRef,
        p1: rdflib.term.URIRef,
        p2: rdflib.term.URIRef,
        o: str,
    ) -> None:
        self.g.remove((s, p1, None))
        self.add_literal_triple(s, p2, o)

    def dump(self, output_file: str | Path | None) -> int:
        if not output_file:
            print('WARNING: You did not specify an output file, no output file created')
            return 1
        self.g.serialize(destination=output_file, format='ttl')
        log_item('Created', output_file)
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.user_story_parser',
        description='Adds any referenced SPARQL file to the graph as text and writes a new Turtle file',
        epilog='Currently only supports turtle.',
        allow_abbrev=False,
    )
    parser.add_argument(
        '--verbose', '-v', help='verbose output', default=False, action='store_true'
    )
    parser.add_argument(
        '--input', '-i', help='The input user-story.ttl file', required=True
    )
    parser.add_argument(
        '--output', '-o', help='The output user-story.ttl file (with embedded SPARQL)'
    )
    kgiri_set_cli_params(parser)
    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)
    set_kgiri_base_replace(args.kgiri_base_replace)

    processor = UserStoryParser(args.input, args.verbose)
    rc = processor.check()
    if rc > 0:
        return rc
    return processor.dump(args.output) if args.output else 1


if __name__ == '__main__':
    main()
