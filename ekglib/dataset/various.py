import gzip
import os
import textwrap
from pathlib import Path

import rdflib
import requests
from rdflib import plugin, Graph
from six import BytesIO

from ..kgiri import EKG_NS
from ..log import log_item, log_rule
from ..mime import MIME_NTRIPLES, MIME_TURTLE
from ..namespace import DATASET
from ..s3 import S3ObjectStore
from ..sparql import SPARQLEndpoint, iter_raw


def set_cli_params(parser):
    ekg_dataset_code = os.getenv('EKG_DATASET_CODE', None)
    # git_branch = os.getenv('GIT_BRANCH', os.getenv('BRANCH_NAME', 'master'))
    group = parser.add_argument_group('Dataset')
    if ekg_dataset_code:
        group.add_argument(
            '--dataset-code',
            help=f'The code of the dataset (default is EKG_DATASET_CODE={ekg_dataset_code})',
            required=True,
            default=ekg_dataset_code
        )
    else:
        group.add_argument(
            '--dataset-code', help='The code of the dataset (can also be set with env var EKG_DATASET_CODE)',
            required=True
        )


#
# TODO: externalize s3os
#
def export_dataset(
        sparql_endpoint: SPARQLEndpoint = None,
        s3_endpoint: S3ObjectStore = None,
        data_source_code: str = None,
        graph_iri: rdflib.URIRef = None,
        mime=MIME_NTRIPLES
) -> bool:
    log_rule(data_source_code)
    log_item("Exporting Dataset", data_source_code)
    log_item("Named Graph IRI", graph_iri.n3())
    r = requests.get(
        sparql_endpoint.endpoint_url(),
        auth=(sparql_endpoint.user_id(), sparql_endpoint.password()),
        params={'graph': graph_iri},
        headers={'Accept': mime},
        stream=True
    )
    sparql_endpoint.handle_error(r)
    content_encoding = r.headers.get('Content-Encoding')
    # log_item("Content Encoding", content_encoding)
    # log_item("Response Encoding", r.encoding)

    log_item('Uploading as', _s3_file_name(mime, data_source_code))
    uploader = s3_endpoint.uploader_for(
        key=_s3_file_name(mime, data_source_code),
        mime=mime,
        content_encoding=content_encoding,
        dataset_code=data_source_code
    )
    chunk_size = 5 * 1024 * 1024  # 5Mb is minimum
    # for chunk in r.iter_lines(chunk_size=chunk_size, decode_unicode=False):
    # for chunk in r.raw.stream(amt=chunk_size, decode_content=None):
    for chunk in iter_raw(r, chunk_size=chunk_size):
        uploader.part(chunk)
    return uploader.complete()


def _s3_file_name(mime, data_source_code):
    if mime == MIME_NTRIPLES:
        return f'ekg-dataset-{data_source_code}.nt.gz'
    return f'ekg-dataset-{data_source_code}.ttl.gz'  # TODO: Support other mime types as well


def export_graph(
        graph: Graph,
        s3_file_name: str,
        s3_endpoint: S3ObjectStore = None,
        data_source_code: str = None
) -> bool:
    """Export the content of the given rdflib.Graph as a Turtle file to the given S3 bucket"""
    log_rule(f"Uploading in-memory graph as {s3_file_name} to S3")
    if Path(s3_file_name).suffix == '.gz':
        content_encoding = 'gzip'
    else:
        content_encoding = None
    uploader = s3_endpoint.uploader_for(
        s3_file_name,
        mime=MIME_TURTLE,
        content_encoding=content_encoding,
        dataset_code=data_source_code
    )
    #
    # Unfortunately this is all happening in memory, the rdflib serializer does not seem
    # to support streaming.
    #
    chunk_max_size = 5 * 1024 * 1024  # 5Mb is minimum
    serializer = plugin.get('ttl', plugin.Serializer)(graph)
    buf = BytesIO()
    with gzip.GzipFile(mode='wb', fileobj=buf) as stream:
        serializer.serialize(stream, encoding="UTF-8")
    chunk = bytearray(chunk_max_size)
    chunk_size = chunk_max_size
    buf.seek(0)

    while chunk_size == chunk_max_size:
        chunk_size = buf.readinto(chunk)
        log_item(f"{s3_file_name} chunk_size", str(chunk_size))
        if chunk_size > 0:
            uploader.part(chunk[0:chunk_size])
    log_item(f"{s3_file_name} completing with", str(chunk_size))
    return uploader.complete()


def datasets_produced_by_pipeline(sparql_endpoint: SPARQLEndpoint, data_source_code: str):
    """
    Return an iterator over the collection of graph iris and the codes of the datasets that the given pipeline
    has produced in the staging database.

    :param sparql_endpoint: the SPARQLEndpoint to use
    :param data_source_code: the code of the data source that the pipeline is for
    :return: iterator over the collection of dataset graph IRIs

    TODO: Also return size
    """

    def _query() -> str:
        return textwrap.dedent(f"""
            PREFIX dataops: <{DATAOPS}>
            PREFIX dataset: <{DATASET}>
            PREFIX kgiri:   <{EKG_NS['KGIRI']}>
            PREFIX kggraph: <{EKG_NS['KGGRAPH']}>
            
            CONSTRUCT {{
                ?pipeline a dataops:Pipeline ;
                    dataset:dataSourceCode ?dataSourceCode
                .
                ?dataset
                    dataops:createdByPipeline ?pipeline ;
                    dataset:inGraph ?graphIRI ;
                    dataset:datasetCode ?datasetCode ;
                    # dataset:numberOfTriples ?numberOfTriples
                .
            }}
            WHERE {{
                GRAPH ?g {{
                    BIND("{data_source_code}" as ?dataSourceCode)
                    ?pipeline a dataops:Pipeline ;
                        dataset:dataSourceCode ?dataSourceCode
                    .
                    ?dataset
                        dataops:createdByPipeline ?pipeline ;
                        dataset:inGraph ?graphIRI ;
                        dataset:datasetCode ?datasetCode
                    .
                }}
                # GRAPH ?graph_iri {{
                    # ?s ?p ?o .
                    # BIND(COUNT(?s) AS ?numberOfTriples)
                # }}
            }}
        """)  # noqa: W293

    log_item('Query', _query())
    g = sparql_endpoint.construct_and_convert(_query())
    for dataset_iri, graph_iri in g.subject_objects(DATASET.inGraph):
        log_item('Dataset IRI', dataset_iri)
        log_item('Graph IRI', graph_iri)
        for dataset_code in g.objects(dataset_iri, DATASET.datasetCode):
            log_item('Dataset Code', dataset_code)
            yield graph_iri, dataset_code
    # exit(1)
    # results = sparql_endpoint.execute_csv_query(query).iter_lines()
    # for graph_iri, dataset_code in [(row['graph_iri'], row['data_source_code']) for row in results]:
    #     # print(f"graph_iri={graph_iri} data_source_code={data_source_code}")
    #     yield rdflib.URIRef(graph_iri), dataset_code
