import os
from pathlib import Path

import mkdocs_gen_files

from ekglib import log_item
from ekglib.log.various import value_error
from ekglib.maturity_model_parser.config import Config
from ekglib.maturity_model_parser.markdown_document import MarkdownDocument


class File(object):
    """Create or open a file, when run in MkDocs use `mkdoc_gen_files`, otherwise normal open()
    """

    def __init__(self, mkdocs: bool, path: Path):
        self.file = None
        self.path = path
        self.mkdocs = mkdocs
        # self.file = self.open(mode='w+')
        # self.file.close()

    @classmethod
    def existing_file(cls, mkdocs: bool, path: Path):
        file = File(mkdocs, path)
        if not file.exists():
            raise value_error(f"File {path} does not exist")
        return file

    def exists(self) -> bool:
        return self.path.exists()

    def open(self, mode: str):
        if self.mkdocs:
            return mkdocs_gen_files.open(self.path, mode, encoding='UTF-8')
        else:
            return open(self.path, mode, encoding='UTF-8')

    def rewrite_all_file(self, data):
        with self.open(mode='w') as self.file:
            self.file.write(data)

    def read_all_content(self):
        with self.open(mode='r') as self.file:
            return self.file.read()

    def append_end(self, data):
        with self.open(mode='a') as self.file:
            self.file.write(data)

    def append_after_second_line(self, data):
        """Write after the file's first line.

        :param str data: is a string containing all the data that is written in the markdown file."""
        with self.open(mode='r+') as self.file:
            file_data = self.file.read()  # Save all the file's content
            self.file.seek(0, 0)  # Place file pointer at the beginning
            first_line = self.file.readline()  # Read the first line
            second_line = self.file.readline()  # Read the second line
            self.file.seek(len(first_line + second_line), 0)  # Place file pointer at the end of the first line
            self.file.write(data)  # Write data
            self.file.write('\n' + file_data[len(first_line + second_line):])

    @classmethod
    def copy(cls, config: Config, from_path: Path, to_path: Path):
        if config.verbose:
            log_item("Copying", f"{from_path} -> {to_path}")
        old_file = File.existing_file(mkdocs=config.mkdocs, path=from_path)
        new_file = File(mkdocs=config.mkdocs, path=to_path)
        new_file.rewrite_all_file(old_file.read_all_content())


def makedirs(path: Path, hint: str):
    log_item(f"{hint} Path", path)
    try:
        os.makedirs(path)
    except FileExistsError:
        return


def copy_template_fragment(from_path: Path, config: Config):
    log_item("Fragment not found", from_path)
    fragment_base = from_path.name
    template_path = config.fragments_root / 'template' / fragment_base
    if not template_path.exists():
        raise value_error(f"Template not found: {template_path}")
    makedirs(from_path.parent, "Fragments")
    File.copy(config=config, from_path=template_path, to_path=from_path)


def copy_fragment(md_file: MarkdownDocument, from_path: Path, config: Config):
    if not from_path.exists():
        copy_template_fragment(from_path=from_path, config=config)
    fragment_base = from_path.name
    log_item("Copying fragment", fragment_base)
    to_path2 = md_file.path.parent / fragment_base
    if config.verbose:
        log_item("to", to_path2)
    File.copy(config=config, from_path=from_path, to_path=to_path2)
    md_file.write(
        "\n\n{% include-markdown \""
        f"{fragment_base}"
        "\" heading-offset=1 %}",
        wrap_width=0
    )
