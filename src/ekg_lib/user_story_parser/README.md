# User Story Parser

```bash
python3 -m ekg_lib.user_story_parser --help
```

```text
usage: python3 -m ekg_lib.user_story_parser [-h] [--verbose] [--input INPUT]
  [--output OUTPUT]

Adds any referenced SPARQL file to the graph as text and writes a new Turtle
file

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         verbose output
  --input INPUT, -i INPUT
                        The input user-story.ttl file
  --output OUTPUT, -o OUTPUT
                        The output user-story-with-sparql.ttl file

Currently only supports turtle.

```

## Links

- [ekg_lib](../../)
- [EKGF](https://ekgf.org)

