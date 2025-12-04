# exceptions

Common exception types and error utilities shared across `ekglib`.

Centralizing these exceptions helps keep error handling consistent between components.

## Exception Classes

### Base Exception

- `Error(Exception)` - Base exception class for all `ekglib` errors

### Specific Exceptions

- `PrefixException(Error)` - Raised when there's an issue with namespace prefixes
- `CannotCapture(Error)` - Raised when data capture operations fail
- `PagingNotSupported(Error)` - Raised when paging is requested but not supported by a data source

## Usage

```python
from ekglib.exceptions import Error, CannotCapture, PagingNotSupported

# Raise custom exceptions
if not can_capture:
    raise CannotCapture("Unable to capture data from source")

# Catch ekglib exceptions
try:
    # some operation
    pass
except Error as e:
    print(f"ekglib error: {e}")
```

## Links

- [ekglib](../)
- [EKGF](https://ekgf.org)
