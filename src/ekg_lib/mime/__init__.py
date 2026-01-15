from ..log import error

# Possible mime types for a query
MIME_TURTLE = 'text/turtle'
MIME_RDFXML = 'application/rdf+xml'
MIME_NTRIPLES = 'application/n-triples'
MIME_TRIG = 'application/trig'
MIME_NQUADS = 'application/n-quads'
MIME_N3 = 'text/n3'
MIME_TRIX = 'application/trix'
MIME_JSONLD = 'application/ld+json'
MIME_SPARQLRESULTS_XML = 'application/sparql_endpoint-results+xml'
MIME_SPARQLRESULTS_JSON = 'application/sparql_endpoint-results+json'
MIME_XBINARY = 'application/x-binary-rdf-results-table'
MIME_BOOLEAN = 'text/boolean'
MIME_CSV = 'text/csv'
MIME_TSV = 'text/tsv'
MIME_TSV2 = 'text/tab-separated-values'
_SPARQL_MIME_TYPES = [
    MIME_TURTLE,
    MIME_RDFXML,
    MIME_NTRIPLES,
    MIME_TRIG,
    MIME_NQUADS,
    MIME_N3,
    MIME_TRIX,
    MIME_JSONLD,
    MIME_SPARQLRESULTS_XML,
    MIME_SPARQLRESULTS_JSON,
    MIME_XBINARY,
    MIME_BOOLEAN,
    MIME_CSV,
    MIME_TSV,
    MIME_TSV2,
]

__all__ = [
    'MIME_TURTLE',
    'MIME_RDFXML',
    'MIME_NTRIPLES',
    'MIME_TRIG',
    'MIME_NQUADS',
    'MIME_N3',
    'MIME_TRIX',
    'MIME_JSONLD',
    'MIME_SPARQLRESULTS_XML',
    'MIME_SPARQLRESULTS_JSON',
    'MIME_XBINARY',
    'MIME_BOOLEAN',
    'MIME_CSV',
    'MIME_TSV',
    'MIME_TSV2',
    'check_sparql_mime_type',
]


def check_sparql_mime_type(mime_type: str) -> bool:
    if mime_type not in _SPARQL_MIME_TYPES:
        error("invalid sparql_endpoint mime type '%s'" % mime_type)
    return True
