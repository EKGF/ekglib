import argparse
from pathlib import Path

import rdflib
from botocore.exceptions import EndpointConnectionError
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from ..data_source import set_cli_params as data_source_set_cli_params
from ..dataset.various import export_graph
from ..git import set_cli_params as git_set_cli_params
from ..kgiri import set_kgiri_base, EKG_NS, set_cli_params as kgiri_set_cli_params
from ..log import error, warning, log, log_item, log_iri, log_error
from ..namespace import RAW
from ..s3 import S3ObjectStore, set_cli_params as s3_set_cli_params
from ..transform_rule_parser import TransformRuleParser, add_transform_rule_namespaces


class TransformRulesCapture:
    """Captures all transform rule files from a given directory and uploads the resulting file to S3
    """
    g: rdflib.Graph

    def __init__(self, args):

        self.args = args
        self.verbose = args.verbose
        self.data_source_code = args.data_source_code
        self.graph_iri = EKG_NS['KGGRAPH'].term(self.data_source_code)
        log_iri('Graph IRI', self.graph_iri)
        self.transform_root = Path(args.transform_root)
        if not self.transform_root.exists():
            error(f"The provided transform root directory does not exist: {self.transform_root}")
        log_item('Git Branch', self.args.git_branch)
        self.g = Graph()
        add_transform_rule_namespaces(self.g)

    def capture(self):
        rules_directories = self.rules_directories_to_capture()
        for directory in rules_directories:
            log_item('Rules Directory', directory.stem)
        for directory in rules_directories:
            self.capture_rules_directory(directory)
        log('Finished Capture Phase')

    def rules_directories_to_capture(self):
        all_rules_directories = [x for x in self.transform_root.iterdir() if x.is_dir()]
        return list(filter(self.filter_rule_directory, all_rules_directories))

    def filter_rule_directory(self, rule_directory):
        stem = rule_directory.stem
        return stem == 'generic' or stem == 'generic-last' or stem == 'obfuscate' or stem == self.data_source_code

    def capture_rules_directory(self, rules_directory: Path):
        rules_directory_iri = EKG_NS['KGIRI'].term("transform-rules-root-directory")
        self.g.add((rules_directory_iri, RDF.type, RAW.term('TransformRulesRoot')))
        log(f'Capturing {rules_directory.stem}-rules:')
        rule_directories = sorted([x for x in rules_directory.iterdir() if x.is_dir()])
        for directory in rule_directories:
            self.capture_rule_directory(directory, rules_directory_iri)

    def capture_rule_directory(self, rule_directory: Path, rules_directory_iri: URIRef):
        log_item('Rule Directory', rule_directory.stem)
        rule_directory_iri = EKG_NS['KGIRI'].term("transform-rule-directory")
        self.g.add((rule_directory_iri, RDF.type, RAW.term('TransformRuleDirectory')))
        self.g.add((rule_directory_iri, RAW.term('inRulesRootDirectory'), rules_directory_iri))
        rule_files = sorted([x for x in rule_directory.iterdir() if x.is_file() and x.suffix == '.ttl'])
        if len(rule_files) == 0:
            warning(f"No rule files found in rule directory {rule_directory}")
            return
        for rule_file in rule_files:
            self.capture_rule_file(rule_file, rule_directory_iri)

    def capture_rule_file(self, rule_file: Path, rule_directory_iri: URIRef):
        log_item('Rule File', f"{rule_file.parent.name}/{rule_file.name}")
        rule_file_iri = EKG_NS['KGIRI'].term("transform-rule-file")
        self.g.add((rule_file_iri, RDF.type, RAW.term('TransformRuleFile')))
        self.g.add((rule_file_iri, RAW.term('inRuleDirectory'), rule_directory_iri))
        processor = TransformRuleParser(
            self.args,
            input_file_name=rule_file,
            rule_file_iri=rule_file_iri
        )
        processor.check()
        for triple in processor.g:
            self.g.add(triple)

    def s3_file_name(self):
        return f"raw-data-transform-rules-{self.data_source_code}.ttl.gz"

    def export(self) -> int:
        try:
            s3os = S3ObjectStore(self.args)
            result = export_graph(
                graph=self.g,
                s3_file_name=self.s3_file_name(),
                s3_endpoint=s3os,
                data_source_code=self.data_source_code  # TODO: Fix export_dataset to become export_graph
            )
            log_item('result', result)
        except EndpointConnectionError:
            log_error("Could not connect to S3 s3_endpoint")
            return False
        return 0 if result else 1


def main():
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.transform_rules_capture',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Captures all transform rule files from a given directory and uploads the resulting file to S3',
        epilog='Currently only supports turtle.',
        allow_abbrev=False
    )
    parser.add_argument('--verbose', '-v', help='verbose output', default=False, action='store_true')
    parser.add_argument('--transform-root', help='The root directory where all rule subdirectories can be found',
                        required=True)
    parser.add_argument('--ontologies-root', help='The root directory where ontologies can be found', required=True)
    git_set_cli_params(parser)
    data_source_set_cli_params(parser)
    kgiri_set_cli_params(parser)
    s3_set_cli_params(parser)
    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)

    processor = TransformRulesCapture(args)
    processor.capture()
    return processor.export()


if __name__ == "__main__":
    exit(main())
