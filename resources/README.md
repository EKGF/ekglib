# resources

Static resources bundled with `ekglib`, such as ontologies and supporting files.

Currently this includes the maturity model ontology in `ontologies/maturity-model.ttl`; see `ontologies/README.md` for more detail.

## Structure

- `ontologies/` - Contains RDF ontology files used by `ekglib`
  - `maturity-model.ttl` - The EKG maturity model ontology

## Usage

These resources are typically accessed programmatically by other `ekglib` components. The ontologies are loaded automatically when needed by parsers and other tools.

## Links

- [ekglib](../)
- [EKGF](https://ekgf.org)
- [Ontologies](ontologies/)
