from __future__ import annotations

import io
import os
import os.path
from pathlib import Path
from typing import Any

import mkdocs_gen_files

from .config import Config
from .markdown_document import MarkdownDocument
from ..log import log_item
from ..log.various import value_error


class File(object):
    """Create or open a file, when run in MkDocs use `mkdoc_gen_files`, otherwise normal open()"""

    def __init__(self, mkdocs: bool, path: Path):
        self.path = path
        self.mkdocs = mkdocs

    @classmethod
    def existing_file(cls, mkdocs: bool, path: Path) -> 'File':
        file = File(mkdocs, path)
        if not file.exists():
            raise value_error(f'File {path} does not exist')
        return file

    def exists(self) -> bool:
        return self.path.exists()

    def open(self, mode: str) -> Any:
        if self.mkdocs:
            return mkdocs_gen_files.open(self.path, mode, encoding='UTF-8')
        else:
            return open(self.path, mode, encoding='UTF-8')

    def rewrite_all_file(self, data: str) -> None:
        makedirs(self.path.parent, 'Generated')
        with self.open(mode='w') as somefile:
            assert isinstance(somefile, io.TextIOWrapper)
            assert somefile.closed is False
            somefile.write(data)

    def read_all_content(self) -> str:
        with self.open(mode='r') as somefile:
            return somefile.read()

    def append_end(self, data: str) -> None:
        with self.open(mode='a') as somefile:
            somefile.write(data)

    def append_after_second_line(self, data: str) -> None:
        """Write after the file's first line.

        :param str data: is a string containing all the data that is written in the markdown file."""
        with self.open(mode='r+') as somefile:
            file_data = somefile.read()  # Save all the file's content
            somefile.seek(0, 0)  # Place file pointer at the beginning
            first_line = somefile.readline()  # Read the first line
            second_line = somefile.readline()  # Read the second line
            somefile.seek(
                len(first_line + second_line), 0
            )  # Place file pointer at the end of the first line
            somefile.write(data)  # Write data
            somefile.write('\n' + file_data[len(first_line + second_line) :])

    @classmethod
    def copy(cls, config: Config, from_path: Path, to_path: Path) -> None:
        if config.verbose:
            log_item('Copying', f'{from_path} -> {to_path}')
        old_file = File.existing_file(mkdocs=config.mkdocs, path=from_path)
        new_file = File(mkdocs=config.mkdocs, path=to_path)
        new_file.rewrite_all_file(old_file.read_all_content())


def makedirs(path: Path, hint: str) -> None:
    log_item(f'{hint} Path', path)
    try:
        os.makedirs(path)
    except FileExistsError:
        return


def copy_template_fragment(from_path: Path, config: Config) -> None:
    log_item('Fragment not found', from_path)
    fragment_base = from_path.name
    template_path = config.fragments_root / 'template' / fragment_base
    if not template_path.exists():
        raise value_error(f'Template not found: {template_path}')
    makedirs(from_path.parent, 'Fragments')
    File.copy(config=config, from_path=template_path, to_path=from_path)


def copy_fragment(
    md_file: MarkdownDocument, from_path: Path, config: Config, indent_prefix: str
) -> None:
    if not from_path.exists():
        copy_template_fragment(from_path=from_path, config=config)
    fragment_base = from_path.name
    log_item('Copying fragment', fragment_base)
    # Copy the fragment file into the same directory as the markdown file...
    to_path2 = md_file.path.parent / fragment_base
    if config.verbose:
        log_item('to', to_path2)
    File.copy(config=config, from_path=from_path, to_path=to_path2)
    # ...but make the include path relative to the docs root so the include-markdown
    # plugin (which resolves paths from docs_dir) can always find it.
    include_path = os.path.relpath(to_path2, config.docs_root)
    md_file.write(
        '\n\n'
        + indent_prefix
        + '{%\n'
        + indent_prefix
        + '  include-markdown "'
        + include_path
        + '"\n'
        + indent_prefix
        + '  heading-offset=1\n'
        + indent_prefix
        + '%}',
        wrap_width=0,
    )


def copy_fragment_new(
    md_file: MarkdownDocument, from_path: Path, config: Config, indent_prefix: str
) -> None:
    if not from_path.exists():
        copy_template_fragment(from_path=from_path, config=config)
    from_path_str = os.path.relpath(
        from_path.resolve().absolute(), config.output_root.resolve().absolute()
    )
    include_file = os.path.relpath(
        from_path_str, os.path.relpath(md_file.path.parent, config.output_root)
    )
    md_file.write(
        '\n\n'
        + indent_prefix
        + '{%\n'
        + indent_prefix
        + '  include-markdown "'
        + include_file
        + '"\n'
        + indent_prefix
        + '  heading-offset=1\n'
        + indent_prefix
        + '%}',
        wrap_width=0,
    )
