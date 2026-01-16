# main

Entry point module that wires together top-level `ekg_lib` behavior.

This package underpins running `ekg_lib` as a module (for example via `python -m ekg_lib.main`) and supports some CLI integrations.

## Main Functions

### RDF File Operations

- `load_rdf_file_into_graph(graph: rdflib.Graph, rdf_file: pathlib.Path)` - Load an RDF file (Turtle format) into an RDF graph
- `load_rdf_stream_into_graph(graph: rdflib.Graph, rdf_stream: BytesIO)` - Load RDF data from a stream into a graph
- `dump_as_ttl_to_stdout(graph: Graph)` - Serialize an RDF graph as Turtle and print to stdout

### Utility Functions

- `is_port_in_use(port)` - Check if a network port is currently in use

## Usage

```python
from rdflib import Graph
from pathlib import Path
from ekg_lib.main import load_rdf_file_into_graph, dump_as_ttl_to_stdout

# Load RDF file into graph
graph = Graph()
load_rdf_file_into_graph(graph, Path("data.ttl"))

# Output graph as Turtle
dump_as_ttl_to_stdout(graph)
```

## Links

- [ekg_lib](../)
- [EKGF](https://ekgf.org)
