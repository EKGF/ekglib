import os
from pathlib import Path

import mkdocs_gen_files
from mdutils import MdUtils

from ekglib import log_item
from ekglib.maturity_model_parser.markdown_document import MarkdownDocument
from ekglib.maturity_model_parser.mdutil_mkdocs import MdUtils4MkDocs


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
    def copy(cls, mkdocs: bool, from_path: Path, to_path: Path):
        log_item("Copying", f"{from_path} -> {to_path}")
        old_file = File.existing_file(mkdocs=mkdocs, path=from_path)
        new_file = File(mkdocs=mkdocs, path=to_path)
        new_file.rewrite_all_file(old_file.read_all_content())



def makedirs(path: Path, hint: str):
    log_item(f"{hint} Path", path)
    try:
        os.makedirs(path)
    except FileExistsError:
        return
