# sparql

Simple helpers for talking to SPARQL endpoints and working with query results.

This package underpins SPARQL-based integrations used by other parts of `ekg_lib`.

## Main Classes

- `SPARQLEndpoint` - Interface for executing SPARQL queries against an endpoint
- `SPARQLResponse` - Wrapper for SPARQL query responses

## Main Functions

### Query Execution

- `SPARQLEndpoint.execute_construct(query: str) -> SPARQLResponse | None` - Execute a CONSTRUCT query
- `SPARQLEndpoint.execute_select(query: str) -> SPARQLResponse | None` - Execute a SELECT query
- `SPARQLEndpoint.endpoint_url() -> str` - Get the endpoint URL
- `SPARQLEndpoint.user_id() -> str | None` - Get authentication user ID
- `SPARQLEndpoint.password() -> str | None` - Get authentication password
- `SPARQLEndpoint.handle_error(response) -> bool` - Handle HTTP errors from endpoint

### Response Processing

- `iter_raw(r: requests.Response, chunk_size: int = 1) -> Any` - Iterate over raw response chunks for streaming

### Utility Functions

- `dump(obj: Any) -> None` - Debug function to dump object attributes
- `set_cli_params(parser: argparse.ArgumentParser) -> None` - Add SPARQL-related CLI arguments

The CLI parameters include:
- `--sparql_endpoint-s3_endpoint` - The SPARQL endpoint URL
- `--sparql_endpoint-database` - The SPARQL database name
- `--sparql_endpoint-userid` - Authentication user ID
- `--sparql_endpoint-passwd` / `--sparql_endpoint-password` - Authentication password

## Usage

```python
from ekg_lib.sparql import SPARQLEndpoint

# Create endpoint
endpoint = SPARQLEndpoint(
    endpoint_url="https://sparql.example.com/query",
    user_id="user",
    password="pass"
)

# Execute CONSTRUCT query
query = """
    PREFIX ex: <http://example.org/>
    CONSTRUCT { ?s ?p ?o }
    WHERE { ?s ?p ?o }
"""
response = endpoint.execute_construct(query)
if response:
    graph = response.convert()  # Convert to rdflib.Graph
```

## Links

- [ekg_lib](../)
- [EKGF](https://ekgf.org)
