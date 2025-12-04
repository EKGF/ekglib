# mime

MIME type constants and helpers used by `ekglib` components that need to work with content types.

This package is typically used indirectly by higher-level tools.

## Main Functions

### Constants

The module provides constants for common MIME types used in RDF and SPARQL operations:

- `MIME_TURTLE` - `text/turtle`
- `MIME_RDFXML` - `application/rdf+xml`
- `MIME_NTRIPLES` - `application/n-triples`
- `MIME_TRIG` - `application/trig`
- `MIME_NQUADS` - `application/n-quads`
- `MIME_N3` - `text/n3`
- `MIME_TRIX` - `application/trix`
- `MIME_JSONLD` - `application/ld+json`
- `MIME_SPARQLRESULTS_XML` - `application/sparql_endpoint-results+xml`
- `MIME_SPARQLRESULTS_JSON` - `application/sparql_endpoint-results+json`
- `MIME_CSV` - `text/csv`
- `MIME_TSV` - `text/tsv`

### Functions

- `check_sparql_mime_type(mime_type: str) -> bool` - Validates that a MIME type is supported for SPARQL operations

## Usage

```python
from ekglib.mime import MIME_TURTLE, check_sparql_mime_type

# Use MIME type constants
content_type = MIME_TURTLE

# Validate MIME types
if check_sparql_mime_type('text/turtle'):
    print("Valid SPARQL MIME type")
```

## Links

- [ekglib](../)
- [EKGF](https://ekgf.org)
