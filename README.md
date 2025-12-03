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

- [Concept Parser](ekglib/concept_parser/)
- [Persona Parser](ekglib/persona_parser/)
- [Story Validate Rule Parser](ekglib/dataops_rule_parser/)
- [Story Vaidate Rules Capture](ekglib/dataops_rules_capture/)
- [Story Validate Rules Executor](ekglib/dataops_rules_execute/)
- [Use Case Parser](ekglib/use_case_parser/)
- [User Story Parser](ekglib/user_story_parser/)

## Capture Steps

- [Xlsx Parser](ekglib/xlsx_parser/)
- [LDAP Parser](ekglib/ldap_parser/)

---

## Installation

```bash
./setup.sh
```

<details>
<summary>⚠️ Troubleshooting: Python3 not linked</summary>

If `python3` was not linked, run:

```bash
brew link --overwrite python
```

</details>

---

## Tests

To run all tests:

```bash
./run-tests.sh
```

To run a single test:

```bash
./run-tests.sh <name of test>
```

---

## Packaging

```bash
uv build
```

