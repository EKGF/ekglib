# ldap_parser_to_file

Helpers for parsing LDAP directories and writing the extracted data to local files.

This component is typically driven via the `ldap_parser_to_file` CLI entrypoint and is used by other tools in `ekglib`.

## Main Functions

- `main()` - Main entry point for the CLI tool

## Usage

This module provides functionality to:

- Connect to LDAP directories
- Parse LDAP entries
- Extract structured data
- Write results to local files

The module is typically invoked as a CLI tool, though the exact command depends on how it's registered in your `pyproject.toml`.

## Links

- [ekglib](../)
- [EKGF](https://ekgf.org)
- Related: [ldap_parser](../ldap_parser/)
