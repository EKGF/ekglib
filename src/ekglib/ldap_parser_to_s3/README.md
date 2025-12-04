# ldap_parser_to_s3

Helpers for parsing LDAP directories and writing the extracted data directly to Amazon S3.

This component is typically driven via the `ldap_parser_to_s3` CLI entrypoint and is used by other tools in `ekglib`.

## Main Functions

- `main()` - Main entry point for the CLI tool

## Usage

This module provides functionality to:
- Connect to LDAP directories
- Parse LDAP entries
- Extract structured data
- Upload results directly to S3

The module integrates with the `ekglib.s3` module for S3 operations and is typically invoked as a CLI tool.

## Links

- [ekglib](../)
- [EKGF](https://ekgf.org)
- Related: [ldap_parser](../ldap_parser/), [s3](../s3/)
