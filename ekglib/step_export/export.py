import argparse

from ..data_source import set_cli_params as data_source_set_cli_params
from ..dataset import datasets_produced_by_pipeline, export_dataset
from ..git import set_cli_params as git_set_cli_params
from ..kgiri import EKG_NS, set_kgiri_base, set_cli_params as kgiri_set_cli_params
from ..log import log_item
from ..mime import MIME_NTRIPLES
from ..s3 import S3ObjectStore, set_cli_params as s3_set_cli_params
from ..sparql import SPARQLEndpoint, set_cli_params as sparql_set_cli_params


class Exporter:
    sparql: SPARQLEndpoint

    def __init__(self, args):
        self.args = args
        self.verbose = args.verbose
        self.data_source_code = args.data_source_code
        self.sparql = SPARQLEndpoint(args)

    def export(self):
        s3os = S3ObjectStore(self.sparql.args)
        for graph_iri, dataset_code in datasets_produced_by_pipeline(self.sparql, self.data_source_code):
            #
            # TODO: For smaller datasets, use MIME_TURTLE, datasets_produced_by_pipeline needs to return size for that
            #
            if export_dataset(
                    sparql_endpoint=self.sparql,
                    s3_endpoint=s3os,
                    graph_iri=graph_iri,
                    data_source_code=dataset_code,
                    mime=MIME_NTRIPLES
            ):
                continue
            return 1
        return 0


def main():
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.step_export',
        description='Export the given named graph from the given staging database to the given S3 bucket',
        epilog='Currently only supports turtle.',
        allow_abbrev=False
    )
    parser.add_argument('--verbose', '-v', help='verbose output', default=False, action='store_true')
    git_set_cli_params(parser)
    kgiri_set_cli_params(parser)
    data_source_set_cli_params(parser)
    sparql_set_cli_params(parser)
    s3_set_cli_params(parser)

    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)

    log_item('KGIRI Base', EKG_NS['KGIRI'])

    exporter = Exporter(args)
    return exporter.export()


if __name__ == "__main__":
    exit(main())
