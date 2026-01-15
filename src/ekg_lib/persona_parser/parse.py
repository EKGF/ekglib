import argparse
from pathlib import Path

import rdflib
from rdflib.namespace import RDF, RDFS

from ..kgiri import kgiri_replace_iri_in_graph, set_kgiri_base, set_kgiri_base_replace
from ..kgiri import set_cli_params as kgiri_set_cli_params
from ..log import error, log_item, warning
from ..namespace import PERSONA


class PersonaParser:
    """gets the IRI of the user story from a given persona.ttl file"""

    def __init__(self, input_file_name: str, verbose: bool) -> None:
        self.verbose = verbose
        self.personaFile = Path(input_file_name)
        if not self.personaFile.exists():
            error('%s does not exist' % input_file_name)
        self.g = rdflib.Graph()
        self.g.parse(location=input_file_name, format='turtle')
        kgiri_replace_iri_in_graph(self.g)
        log_item('Number of triples', len(self.g))
        if self.verbose:
            for s, p, o in self.g:
                print((s, p, o))

    def check(self) -> None:
        for persona in self.g.subjects(RDF.type, PERSONA.Persona):
            log_item('Persona', persona)
            for rdfsLabel in self.g.objects(persona, RDFS.label):
                log_item('Persona Title', rdfsLabel)
        #
        # TODO: Nothing much happens here yet
        #

    def dump(self, output_file: str | Path | None) -> int:
        if not output_file:
            warning('You did not specify an output file, no output file created')
            return 1
        self.g.serialize(destination=output_file, format='ttl')
        log_item('Created', output_file)
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='python3 -m ekg_lib.personas',
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
        help='The input .ttl file containing the definition of the persona',
    )
    parser.add_argument('--output', '-o', help='The output file')
    kgiri_set_cli_params(parser)
    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)
    set_kgiri_base_replace(args.kgiri_base_replace)

    processor = PersonaParser(args.input, args.verbose)
    processor.check()
    processor.dump(args.output)
    return processor.dump(args.output) if args.output else 1


if __name__ == '__main__':
    exit(main())
if __name__ == '__main__':
    exit(main())
