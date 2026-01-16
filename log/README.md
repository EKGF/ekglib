# log

Logging helpers and configuration used across `ekg_lib`.

These utilities standardize logging behavior for the various parsers, pipelines, and tools.

## Main Functions

### Basic Logging

- `log(msg: str) -> None` - Log a general message
- `log_error(msg: str) -> None` - Log an error message
- `warning(msg: str) -> None` - Log a warning message
- `error(msg: str) -> None` - Log an error (may raise exception)
- `eprint(*args: Any, **kwargs: Any) -> None` - Print to stderr

### Structured Logging

- `log_item(item: str, msg: Any) -> None` - Log a key-value pair
- `log_rule(msg: str) -> None` - Log a rule or processing step
- `log_list(item: str, list_: Any) -> None` - Log a list of items
- `log_iri(item: str, iri: str) -> None` - Log an IRI with proper formatting
- `log_resource(graph: Graph, subject: Any) -> None` - Log details about an RDF resource
- `log_dump(item: str, object_: Any) -> None` - Dump object details for debugging
- `log_exception(e: Exception | None = None) -> None` - Log exception details

### Error Handling

- `value_error(*args: Any) -> ValueError` - Create a ValueError with formatted message

## Usage

```python
from ekg_lib.log import log, log_item, log_iri, log_error

# Basic logging
log("Processing started")
log_item("Dataset", "my-dataset")
log_iri("Graph IRI", "https://kg.example.com/graph/123")

# Error logging
try:
    # some operation
    pass
except Exception as e:
    log_error(f"Operation failed: {e}")
```

## Links

- [ekg_lib](../)
- [EKGF](https://ekgf.org)
