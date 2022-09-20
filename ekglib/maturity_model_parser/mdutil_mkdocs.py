from __future__ import annotations
from mdutils import MdUtils

from .MarkdownFileForMkDocs import MarkDownFileForMkDocs


class MdUtils4MkDocs(MdUtils):

    def create_md_file(self):
        """It creates a new Markdown file.
        :return: return an instance of a MarkDownFile."""
        md_file = MarkDownFileForMkDocs(self.file_name)
        md_file.rewrite_all_file(
            data=self.title + self.table_of_contents + self.file_data_text + self.reference.get_references_as_markdown()
        )
        return md_file

    def read_md_file(self, file_name):
        """Reads a Markdown file and save it to global class `file_data_text`.

        :param file_name: Markdown file's name that has to be read.
        :type file_name: str
        :return: optionally returns the file data content.
        :rtype: str
        """
        file_data = MarkDownFileForMkDocs().read_file(file_name)
        self.___update_file_data(file_data)

        return file_data
