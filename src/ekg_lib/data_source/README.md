# data_source

Abstractions and helpers for describing and working with input data sources in `ekg_lib` pipelines and parsers.

This package provides a small set of reusable building blocks used across multiple components.

## Main Functions

### CLI Integration

- `set_cli_params(parser: ArgumentParser) -> Any` - Add data source-related CLI arguments (`--data-source-code`)

The CLI parameter reads from environment variable `EKG_DATA_SOURCE_CODE` if set.

## Usage

```python
from argparse import ArgumentParser
from ekg_lib.data_source import set_cli_params

parser = ArgumentParser()
set_cli_params(parser)
args = parser.parse_args()

# Access the data source code
print(f"Data source: {args.data_source_code}")
```

## Links

- [ekg_lib](../)
- [EKGF](https://ekgf.org)
