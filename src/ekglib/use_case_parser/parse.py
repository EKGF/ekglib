import argparse
from pathlib import Path

import rdflib
from rdflib.namespace import RDF, RDFS

from ..kgiri import (
    set_kgiri_base,
    set_kgiri_base_replace,
    set_cli_params as kgiri_set_cli_params,
    kgiri_replace_iri_in_graph,
)
from ..log import log_item, error, warning
from ..namespace import USECASE


class UseCaseParser:
    """
    gets the IRI of the user story from a given use-case.ttl file
    """

    def __init__(self, input_file_name, verbose):
        self.verbose = verbose
        self.useCaseFile = Path(input_file_name)
        if not self.useCaseFile.exists():
            error(f'File {input_file_name} does not exist')
        self.g = rdflib.Graph()
        self.g.parse(location=input_file_name, format='turtle')
        kgiri_replace_iri_in_graph(self.g)
        log_item('Number of triples', len(self.g))
        if self.verbose:
            for s, p, o in self.g:
                print((s, p, o))

    def check(self):
        for useCase in self.g.subjects(RDF.type, USECASE.UseCase):
            log_item('Use Case', useCase)
            for rdfsLabel in self.g.objects(useCase, RDFS.label):
                log_item('Use Case Title', rdfsLabel)
        #
        # TODO: Nothing much happens here yet
        #

    def dump(self, output_file):
        if not output_file:
            warning('You did not specify an output file, no output file created')
            return
        self.g.serialize(destination=output_file, format='ttl')
        log_item('Created', output_file)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.use_case_parser',
        description='Checks a use case RDF file',
        epilog='Currently only supports turtle.',
        allow_abbrev=False,
    )
    parser.add_argument(
        '--verbose', '-v', help='verbose output', default=False, action='store_true'
    )
    parser.add_argument(
        '--input',
        '-i',
        help='The input .ttl file containing the definition of the use case',
    )
    parser.add_argument('--output', '-o', help='The output file')
    kgiri_set_cli_params(parser)
    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)
    set_kgiri_base_replace(args.kgiri_base_replace)

    processor = UseCaseParser(args.input, args.verbose)
    processor.check()
    processor.dump(args.output)
    return processor.dump(args.output) if args.output else 1


if __name__ == '__main__':
    exit(main())
