# exceptions

Common exception types and error utilities shared across `ekg_lib`.

Centralizing these exceptions helps keep error handling consistent between components.

## Exception Classes

### Base Exception

- `Error(Exception)` - Base exception class for all `ekg_lib` errors

### Specific Exceptions

- `PrefixException(Error)` - Raised when there's an issue with namespace prefixes
- `CannotCapture(Error)` - Raised when data capture operations fail
- `PagingNotSupported(Error)` - Raised when paging is requested but not supported by a data source

## Usage

```python
from ekg_lib.exceptions import Error, CannotCapture, PagingNotSupported

# Raise custom exceptions
if not can_capture:
    raise CannotCapture("Unable to capture data from source")

# Catch ekg_lib exceptions
try:
    # some operation
    pass
except Error as e:
    print(f"ekg_lib error: {e}")
```

## Links

- [ekg_lib](../)
- [EKGF](https://ekgf.org)
