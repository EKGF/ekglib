# dataset

Helpers and types for representing datasets used by `ekg_lib` tools and pipelines.

These utilities are typically consumed by higher-level parsers and exporters rather than used directly.

## Main Functions

### CLI Integration

- `set_cli_params(parser: argparse.ArgumentParser) -> None` - Add dataset-related CLI arguments (`--dataset-code`)

The CLI parameter reads from environment variable `EKG_DATASET_CODE` if set.

### Dataset Export

- `export_dataset(sparql_endpoint: SPARQLEndpoint | None, s3_endpoint: S3ObjectStore | None, data_source_code: str | None, graph_iri: rdflib.URIRef | None, mime=MIME_NTRIPLES) -> bool` - Export a dataset from a SPARQL endpoint to S3
- `export_graph(graph: Graph, s3_file_name: str, s3_endpoint: S3ObjectStore | None, data_source_code: str | None) -> bool` - Export an in-memory RDF graph to S3 as a Turtle file
- `datasets_produced_by_pipeline(sparql_endpoint: SPARQLEndpoint, data_source_code: str)` - Return an iterator over datasets produced by a pipeline in the staging database

## Usage

```python
from ekg_lib.dataset import export_dataset, export_graph
from ekg_lib.sparql import SPARQLEndpoint
from ekg_lib.s3 import S3ObjectStore
from rdflib import URIRef

# Export dataset from SPARQL to S3
success = export_dataset(
    sparql_endpoint=sparql_endpoint,
    s3_endpoint=s3_endpoint,
    data_source_code="my-source",
    graph_iri=URIRef("https://kg.example.com/graph/123")
)

# Export in-memory graph to S3
success = export_graph(
    graph=my_graph,
    s3_file_name="output.ttl.gz",
    s3_endpoint=s3_endpoint,
    data_source_code="my-source"
)
```

## Links

- [ekg_lib](../)
- [EKGF](https://ekgf.org)
