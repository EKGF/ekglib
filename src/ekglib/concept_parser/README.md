# Concept Parser

The Concept Parser reads the given Turtle input file and loads each concept into
an in-memory graph (based on `rdflib` with a reasoner based on `owlrl`).
The inferred results will be written to the given output file.

> **Note:** This is an extremly basic implementation, much more to come here.

```bash
python3 -m ekglib.concept_parser --help
```

```text
usage: python3 -m ekglib.concepts [-h] [--verbose] [--input INPUT] [--output OUTPUT] [--kgiri-base KGIRI_BASE]

Checks a use case RDF file

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         verbose output
  --input INPUT, -i INPUT
                        The input .ttl file containing the definition of the concepts
  --output OUTPUT, -o OUTPUT
                        The output file

KGIRI:
  --kgiri-base KGIRI_BASE
                        A root level URL to be used for all KGIRI types (default is EKG_KGIRI_BASE=https://kg.your-company.kom/)

Currently only supports turtle.
```

## Links

- [ekglib](../../)
- [EKGF](https://ekgf.org)

