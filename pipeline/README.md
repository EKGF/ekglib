# pipeline

Lightweight pipeline framework used by `ekg_lib` to define and run data processing steps.

Key pieces include:

- Decorators for declaring pipeline steps.
- An example pipeline in `example.py`, exposed via the `pipeline-example` console script.

See the top-level `ekg_lib` README for installation and how to invoke the CLI entrypoints.

## CLI Entry Points

- `pipeline-example` - Run the example pipeline (defined in `example.py`)

## Main Components

### Decorators

- Pipeline step decorators for defining processing stages

### Example Pipeline

The `example.py` module provides a reference implementation showing how to:
- Define pipeline steps
- Process data through multiple stages
- Handle errors and logging

## Usage

```bash
# Run the example pipeline
pipeline-example --help
pipeline-example [options]
```

Or programmatically:

```python
from ekg_lib.pipeline.example import main

# Run the example pipeline
main()
```

## Links

- [ekg_lib](../)
- [EKGF](https://ekgf.org)
