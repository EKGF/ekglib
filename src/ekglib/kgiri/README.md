# kgiri

Utilities for constructing and working with IRIs and related concepts in executable knowledge graphs.

These helpers are used throughout `ekglib` to keep knowledge graph identifiers consistent and well-structured.

## Main Functions

### IRI Generation

- `kgiri_random() -> URIRef` - Generate a random KGIRI using a UUID
- `kgiri_with(key: str) -> URIRef` - Create a KGIRI from a given key string
- `parse_identity_key(legacy_id: Any) -> str` - Parse a legacy identifier into a normalized key
- `parse_identity_key_with_prefix(prefix: str, legacy_id: Any) -> str` - Parse an identifier with a prefix

### Namespace Management

- `set_ekg_namespace(key: str, iri: str) -> None` - Set an EKG namespace mapping
- `set_ekg_namespace_with_base(key: str, base: str, suffix: str) -> None` - Set namespace with base and suffix
- `set_kgiri_base(ekg_kgiri_base: Optional[str]) -> None` - Set the base IRI for KGIRI generation
- `set_kgiri_base_replace(ekg_kgiri_base_replace: Optional[str]) -> None` - Set replacement base for KGIRI
- `complete_ns_iri_ending(iri)` - Complete a namespace IRI ending

### IRI Replacement

- `kgiri_replace(value: Any) -> Any` - Replace IRIs in a value using the configured base
- `kgiri_replace_iri_in_graph(g: Graph) -> None` - Replace IRIs throughout an RDF graph
- `kgiri_replace_iri_in_literal(value: Literal) -> Literal` - Replace IRIs in an RDF literal

### CLI Integration

- `set_cli_params(parser: argparse.ArgumentParser) -> Any` - Add KGIRI-related CLI arguments (`--kgiri-base`, `--kgiri-base-replace`)

## Usage

```python
from ekglib.kgiri import kgiri_with, kgiri_random, set_kgiri_base

# Set the base IRI (typically via environment variable EKG_KGIRI_BASE)
set_kgiri_base("https://kg.your-company.kom/")

# Generate IRIs
iri1 = kgiri_with("person/12345")
iri2 = kgiri_random()  # Uses UUID
```

## Links

- [ekglib](../)
- [EKGF](https://ekgf.org)
