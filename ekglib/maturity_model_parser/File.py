from pathlib import Path

import mkdocs_gen_files


class File(object):
    """Create a file, when run in MkDocs use `mkdoc_gen_files`, otherwise normal open()
    """

    def __init__(self, mkdocs: bool, path: Path):
        self.file = None
        self.path = path
        self.mkdocs = mkdocs
        self.file = self.open(mode='w+')
        self.file.close()

    def open(self, mode: str):
        if self.mkdocs:
            return mkdocs_gen_files.open(self.path, mode, encoding='UTF-8')
        else:
            return open(self.path, mode, encoding='UTF-8')

    def rewrite_all_file(self, data):
        with self.open(mode='w') as self.file:
            self.file.write(data)

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


