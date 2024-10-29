import pathlib
from io import BytesIO

import rdflib
from rdflib import Graph, plugin

from ..kgiri import kgiri_replace_iri_in_graph
from ..log import log_item
from ..log.various import value_error


def load_rdf_file_into_graph(graph: rdflib.Graph, rdf_file: pathlib.Path):
    if not rdf_file.exists():
        raise value_error(f'File does not exist: {rdf_file}')
    with rdf_file.open() as f:
        graph.parse(source=f, format='turtle')  # TODO: support any RDF file
        kgiri_replace_iri_in_graph(graph)


def load_rdf_stream_into_graph(graph: rdflib.Graph, rdf_stream: BytesIO):
    graph.parse(
        source=rdf_stream, format='turtle'
    )  # TODO: support any RDF file. # noqa: E501
    kgiri_replace_iri_in_graph(graph)


def dump_as_ttl_to_stdout(graph: Graph):
    serializer = plugin.get('ttl', plugin.Serializer)(graph)
    stream = BytesIO()
    log_item('Base', graph.base)
    serializer.serialize(stream, encoding='UTF-8')
    print(stream.getvalue().decode('UTF-8'))


#
# See https://stackoverflow.com/questions/2470971/fast-way-to-test-if-a-port-is-in-use-using-python # noqa: E501
#
def is_port_in_use(port):
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
