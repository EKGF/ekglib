import argparse
from pathlib import Path

import rdflib
from rdflib.namespace import RDF, RDFS

from ..kgiri import set_kgiri_base, set_cli_params as kgiri_set_cli_params
from ..log import error, log_item, warning
from ..namespace import CONCEPT


class ConceptParser:
    """gets the IRIs of all the concepts from a given concepts.ttl file"""

    def __init__(self, input_file_name, verbose):

        self.verbose = verbose
        self.conceptsFile = Path(input_file_name)
        if not self.conceptsFile.exists():
            error("%s does not exist" % input_file_name)
        self.g = rdflib.Graph()
        self.g.parse(location=input_file_name, format='turtle')
        log_item("Number of triples", len(self.g))
        if self.verbose:
            for s, p, o in self.g:
                print((s, p, o))

    def check(self):
        for concept in self.g.subjects(RDF.type, CONCEPT.Concept):
            log_item("Concept", concept)
            for rdfsLabel in self.g.objects(concept, RDFS.label):
                log_item("Concept Title", rdfsLabel)
            for key in self.g.objects(concept, CONCEPT.key):
                log_item("Concept Key", key)
        #
        # TODO: Nothing much happens here yet
        #

    def dump(self, output_file):
        if not output_file:
            warning("You did not specify an output file, no output file created")
            return
        self.g.serialize(destination=output_file, format='ttl')
        log_item("Created", output_file)


def main():
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.concepts',
        description='Checks a use case RDF file',
        epilog='Currently only supports turtle.',
        allow_abbrev=False
    )
    parser.add_argument('--verbose', '-v', help='verbose output', default=False, action='store_true')
    parser.add_argument('--input', '-i', help='The input .ttl file containing the definition of the concepts')
    parser.add_argument('--output', '-o', help='The output file')
    kgiri_set_cli_params(parser)
    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)

    processor = ConceptParser(args.input, args.verbose)
    processor.check()
    processor.dump(args.output)
    return processor.dump(args.output) if args.output else 1


if __name__ == "__main__":
    exit(main())
