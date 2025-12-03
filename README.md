# ekglib

> ⚠️ **Warning:** This is a pre-alpha project. Everything in this repo is subject to heavy change.

A Python Library for various tasks in an EKG DataOps operation.

## Badges

[![Build & Test](https://github.com/EKGF/ekglib/workflows/Build%20&%20Test/badge.svg)](https://github.com/EKGF/ekglib/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-package%20manager-blue)](https://github.com/astral-sh/uv)
[![Linting & Formatting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://mypy.readthedocs.io/)

**Links:**

- 📖 [Documentation](https://ekgf.github.io/ekglib/)
- 🐛 [Issue Tracker](https://github.com/EKGF/ekglib/issues)
- 💬 [Discussions](https://github.com/EKGF/ekglib/discussions)

---

## Metadata Parsers

- [Concept Parser](concept_parser/)
- [Persona Parser](persona_parser/)
- [Story Validate Rule Parser](dataops_rule_parser/)
- [Story Vaidate Rules Capture](dataops_rules_capture/)
- [Story Validate Rules Executor](dataops_rules_execute/)
- [Use Case Parser](use_case_parser/)
- [User Story Parser](user_story_parser/)

## Capture Steps

- [Xlsx Parser](xlsx_parser/)
- [LDAP Parser](ldap_parser/)

---

## Installation

**Using `uv` (recommended)**

If you are using `uv` to manage your project, add `ekglib` as a dependency:

```bash
uv add ekglib
```

You can then run the provided CLI tools via `uv`:

```bash
uv run xlsx-parser --help
uv run user-story-parser --help
uv run pipeline-example --help
```

To install the CLI tools as global commands (similar to `pipx`):

```bash
uv tool install ekglib

xlsx-parser --help
user-story-parser --help
pipeline-example --help
```

**Using `pip`**

If you prefer to use `pip` directly:

```bash
python -m pip install ekglib
```

The console scripts will then be available on your `PATH`:

```bash
xlsx-parser --help
user-story-parser --help
pipeline-example --help
```

---

## Development setup (from source)

If you cloned this repository and want to work on `ekglib` itself:

```bash
uv sync
```

This will create and populate a virtual environment using `uv` based on `pyproject.toml`.

---

## Tests

To run all tests:

```bash
uv run pytest
```

To run a single test:

```bash
uv run pytest tests/<path-to-test> -k <name-of-test>
```

---

## Packaging

```bash
uv build
```

