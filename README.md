# ekg-lib

A Python Library for various tasks in an EKG DataOps operation.

## Badges

[![PyPI version](https://badge.fury.io/py/ekg-lib.svg)](https://pypi.org/project/ekg-lib/)
[![Build & Test](https://github.com/EKGF/ekg-lib/workflows/Build%20&%20Test/badge.svg)](https://github.com/EKGF/ekg-lib/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-package%20manager-blue)](https://github.com/astral-sh/uv)
[![Linting & Formatting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://mypy.readthedocs.io/)

## Metadata Parsers

- [Concept Parser](concept_parser/README.md)
- [Persona Parser](persona_parser/README.md)
- [Story Validate Rule Parser](dataops_rule_parser/README.md)
- [Story Validate Rules Capture](dataops_rules_capture/README.md)
- [Story Validate Rules Executor](dataops_rules_execute/README.md)
- [Use Case Parser](use_case_parser/README.md)
- [User Story Parser](user_story_parser/README.md)

## Capture Steps

- [Xlsx Parser](xlsx_parser/README.md)
- [LDAP Parser](ldap_parser/README.md)

## Maturity Model Tools

- [Maturity Model Parser](maturity_model_parser/README.md)

## Pipelines and Export

- [Pipeline Framework](pipeline/README.md)
- [Step Export](step_export/README.md)

## LDAP Variants

- [LDAP Parser to File](ldap_parser_to_file/README.md)
- [LDAP Parser to S3](ldap_parser_to_s3/README.md)

## Storage and Data Access

- [S3 Helpers](s3/README.md)
- [Data Sources](data_source/README.md)
- [Datasets](dataset/README.md)

## Knowledge Graph and SPARQL Utilities

- [KG IRI Utilities](kgiri/README.md)
- [SPARQL Helpers](sparql/README.md)
- [Namespaces](namespace/README.md)
- [Ontologies and Resources](resources/README.md)

## Core Utilities

- [Logging Utilities](log/README.md)
- [String Utilities](string/README.md)
- [Git Utilities](git/README.md)
- [Exceptions](exceptions/README.md)
- [MIME Helpers](mime/README.md)
- [Main CLI Entrypoint](main/README.md)

## Installation

### From PyPI (recommended)

```bash
pip install ekg-lib
```

Or using `uv`:

```bash
uv add ekg-lib
```

### From GitHub

Add `ekg-lib` as a dependency from GitHub:

```bash
uv add --git https://github.com/EKGF/ekg-lib.git
```

Or using `pip`:

```bash
pip install "git+https://github.com/EKGF/ekg-lib.git"
```

### CLI tools

After installation, the following CLI tools are available:

```bash
xlsx-parser --help
user-story-parser --help
pipeline-example --help
```

To install as global commands using `uv`:

```bash
uv tool install ekg-lib
```

## Development setup (from source)

If you cloned this repository and want to work on `ekg-lib` itself:

```bash
uv sync
```

This creates a virtual environment using `uv` based on `pyproject.toml`.

## Tests

To run all tests:

```bash
uv run pytest
```

To run a single test:

```bash
uv run pytest tests/<path-to-test> -k <name-of-test>
```

## Packaging

```bash
uv build
```
