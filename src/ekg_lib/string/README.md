# string

String utility functions used throughout `ekg_lib`, including case conversion and predicate helpers.

These helpers are shared by multiple higher-level components.

## Main Functions

### Case Conversion

- `is_lower_camel_case(some_string: str) -> bool` - Check if a string is in lowerCamelCase format

### Prefix/Suffix Operations

- `common_prefix(items: Union[tuple, list, str]) -> str` - Find the common prefix of multiple strings
- `common_suffix(items: Union[tuple, list, str]) -> str` - Find the common suffix of multiple strings
- `remove_prefix(text: str, prefix_: str) -> str` - Remove a prefix from a string if present
- `strip_end(text: str, suffix: str) -> str` - Remove a suffix from a string if present

### List/String Conversion

- `argv_list(param_values: list[str]) -> str` - Convert a list of strings to a command-line argument string
- `argv_check_list(param_values: Any) -> list[Any]` - Validate and convert parameter values to a list

### Column/Predicate Parsing

- `parse_column_name(column_name: str | int | Any) -> str | None` - Parse a column name from various input types

### Binary Conversion

- `str_to_binary(s: str) -> bytes` - Convert a string to bytes

## Usage

```python
from ekg_lib.string import (
    common_prefix,
    remove_prefix,
    parse_column_name,
    is_lower_camel_case
)

# Find common prefix
prefix = common_prefix(["prefix1_value", "prefix1_other"])  # Returns "prefix1_"

# Remove prefix
result = remove_prefix("prefix_value", "prefix_")  # Returns "value"

# Parse column names
col = parse_column_name("column_name")  # Returns "column_name"
col = parse_column_name(5)  # Returns "5"

# Check case
is_camel = is_lower_camel_case("lowerCamelCase")  # Returns True
```

## Links

- [ekg_lib](../)
- [EKGF](https://ekgf.org)
