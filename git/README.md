# git

Helpers for interacting with Git repositories from within `ekg_lib` tools.

These utilities are used where Git metadata needs to be inspected or recorded as part of a workflow.

## Main Functions

### CLI Integration

- `set_cli_params(parser: ArgumentParser) -> None` - Add Git-related CLI arguments (`--git-branch` / `--branch`)

The CLI parameter reads from environment variables `GIT_BRANCH` or `BRANCH_NAME`, defaulting to `'main'` if neither is set.

## Usage

```python
from argparse import ArgumentParser
from ekg_lib.git import set_cli_params

parser = ArgumentParser()
set_cli_params(parser)
args = parser.parse_args()

# Access the git branch
print(f"Current branch: {args.git_branch}")
```

## Links

- [ekg_lib](../)
- [EKGF](https://ekgf.org)
