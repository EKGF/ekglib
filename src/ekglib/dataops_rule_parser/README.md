# Rule Parser

> **Warning:** TODO

```bash
python3 -m ekglib.dataops_rule_parser --help
```

```text
usage: python3 -m ekglib.dataops_rule_parser [-h] [--verbose]
  [--input INPUT]
  [--output OUTPUT]
  [--ontologies-root ONTOLOGIES_ROOT]

Adds any referenced SPARQL file to the graph as text and writes a new Turtle
file

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         verbose output
  --input INPUT, -i INPUT
                        The input rule.ttl file
  --output OUTPUT, -o OUTPUT
                        The output rule-with-sparql.ttl file
  --ontologies-root ONTOLOGIES_ROOT
                        The root directory where ontologies can be found

Currently only supports turtle.
```

## Links

- [ekglib](../../)
- [EKGF](https://ekgf.org)

