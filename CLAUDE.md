# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when
working with code in this repository.

## Project overview

ekg-lib is a Python library for Enterprise Knowledge Graph (EKG)
DataOps operations. It provides metadata parsers that transform
Excel/documents to RDF, data capture tools, and knowledge graph
utilities. The library focuses on semantic data representation
using RDF and SPARQL.

## Commands

### Installation

```bash
uv sync                   # Install Python dependencies (creates .venv)
npm install               # Install Node.js dev tools (husky, commitlint, markdownlint)
make install              # Full setup (Homebrew packages + Python via uv)
```

### Testing

```bash
uv run pytest                              # Run all tests
uv run pytest tests/<path> -k <name>       # Run specific test
uv run pytest --run-triple_store           # With SPARQL (localhost:5820)
uv run pytest --run-object_store           # With S3 (localhost:9000)
uv run pytest --run-ldap                   # With external LDAP
```

### Linting and formatting

```bash
uv run ruff format .              # Format Python code
uv run ruff check .               # Lint Python code
uv run ruff check --fix .         # Auto-fix linting issues
uv run mypy src                   # Type checking
npm run lint:md                   # Lint markdown files
make check                        # Format check + lint
```

### Building

```bash
uv build                          # Build distribution packages
```

### CLI tools

```bash
uv run xlsx-parser --help
uv run user-story-parser --help
uv run pipeline-example --help
```

## Architecture

### Module organization (`src/ekg_lib/`)

**Metadata parsers** - Transform documents to RDF:

- `concept_parser/`, `persona_parser/`, `user_story_parser/`,
  `use_case_parser/`
- `dataops_rule_parser/`, `dataops_rules_capture/`,
  `dataops_rules_execute/`
- `maturity_model_parser/`

**Data capture**:

- `xlsx_parser/` - Excel to RDF
- `ldap_parser/`, `ldap_parser_to_file/`, `ldap_parser_to_s3/` -
  LDAP directory parsing

**Knowledge graph core**:

- `kgiri/` - Knowledge Graph IRI generation and management
- `namespace/` - RDF namespace definitions (DATAOPS, USERSTORY,
  RULE, DATASET, PERSONA, CONCEPT, RAW)
- `sparql/` - SPARQL query helpers
- `resources/` - Bundled ontologies

**Storage**:

- `s3/` - AWS S3 utilities
- `data_source/`, `dataset/` - Data abstractions

**Utilities**:

- `log/` - Structured logging
- `string/`, `git/`, `exceptions/`, `mime/`, `main/`

**Pipeline framework** (`pipeline/`):

- Async generator-based pipelines using decorators
  (`@async_source`, `@async_step`)
- Supports data flow with priming and state management

### Key patterns

1. **Parser pattern**: Parse document -> Extract data ->
   Generate RDF triples -> Serialize to Turtle (.ttl)
2. **CLI entry points**: Functions named `main()` returning int
   status codes, using argparse
3. **Module exports**: Each module has `__init__.py` with explicit
   `__all__` definitions
4. **RDF focus**: Heavy use of rdflib, custom EKGF namespaces,
   IRI generation utilities

## Critical conventions

### Python setup

- Python 3.14.2+ (see `.python-version`)
- `uv` package manager
- Ruff for linting/formatting (single quotes, 120 char line length)
- mypy strict mode for type checking
- Test timeout: 10 seconds per test

### Markdown formatting

- **70-character line length** (configured in `.markdownlint.json`
  and `.prettierrc.json`)
- Use `-` for unordered lists
- Sentence case for headers (not Title Case)

### Git workflow

- **NEVER execute `git push`** - users must push manually
- **NEVER bypass hooks** with `--no-verify`
- **NEVER use `git merge`** - always use `git rebase` for
  linear history
- Commit only when explicitly requested
- Use Angular Conventional Commits: `<type>(<scope>): <subject>`
  - Types: `build`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`,
    `revert`, `style`, `test`
  - Scope is required (e.g., `feat(parser):`, `fix(ui):`)
  - All lowercase, imperative mood, no period at end
  - Note: `chore` is NOT allowed in Angular convention

### Pre-commit hooks

Husky runs on commit:

- **commit-msg**: Validates commit message format (commitlint)
- **pre-commit**: Lints staged Python files (ruff) and
  Markdown files (markdownlint)

### Multi-line commit messages

Use multiple `-m` flags to avoid body-max-line-length violations:

```bash
git commit -m "feat(component): add xyz" \
           -m "Short descriptive line"
```

## Test markers

Tests requiring external services use pytest markers:

- `@pytest.mark.triple_store` - SPARQL endpoint tests
- `@pytest.mark.object_store` - S3 endpoint tests
- `@pytest.mark.ldap` - LDAP tests

## Dependencies

- Python 3.14.2+ with `uv` package manager
- Node.js for dev tools (commitlint, markdownlint, prettier)
- `rdflib`, `SPARQLWrapper`, `owlrl` - RDF/Knowledge Graph
- `pandas`, `openpyxl` - Data processing
- `boto3` - AWS S3
- `ldap3` - LDAP protocol
