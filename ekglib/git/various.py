import os


def set_cli_params(parser):
    git_branch = os.getenv('GIT_BRANCH', os.getenv('BRANCH_NAME', 'main'))
    parser.add_argument(
        '--git-branch', '--branch',
        help=f'The git branch name we\'re working on, default {git_branch}',
        default=git_branch
    )
