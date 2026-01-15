# namespace

Central definitions of RDF namespaces and prefixes used throughout `ekg_lib`.

This package keeps URIs and prefixes consistent across different modules and tools.

## Defined Namespaces

The module defines `rdflib.Namespace` objects for common ontologies:

- `MATURITY_MODEL` - `https://raw.githubusercontent.com/EKGF/ontology-maturity-model/main/maturity-model.ttl#`
- `USERSTORY` - `https://ekgf.org/ontology/user-story/`
- `RULE` - `https://ekgf.org/ontology/dataops-rule/`
- `DATAOPS` - `https://ekgf.org/ontology/dataops/`
- `DATASET` - `https://ekgf.org/ontology/dataset/`
- `USECASE` - `https://ekgf.org/ontology/use-case/`
- `PERSONA` - `https://ekgf.org/ontology/persona/`
- `CONCEPT` - `https://ekgf.org/ontology/concept/`
- `EKGPSS` - `https://ekgf.org/ontology/ekg-platform-story-service/`
- `LDAP` - `https://ekgf.org/ontology/ldap/`
- `PROV` - `http://www.w3.org/ns/prov#` (PROV-O)
- `RAW` - `https://ekgf.org/ontology/raw/`

## Constants

- `BASE_IRI_MATURITY_MODEL` - `'https://maturity.ekgf.org/id/'`

## Usage

```python
from ekg_lib.namespace import DATASET, DATAOPS, CONCEPT

# Use namespaces to create URIs
dataset_uri = DATASET.datasetCode
pipeline_uri = DATAOPS.Pipeline
concept_uri = CONCEPT.Concept
```

## Links

- [ekg_lib](../)
- [EKGF](https://ekgf.org)
