#
# Initial version of this code has been copied from https://github.com/didix21/mdutils
#
from __future__ import annotations

from pathlib import Path
from textwrap import fill

import mdutils.tools.Table
import mdutils.tools.TableOfContents
from mdutils.fileutils.fileutils import MarkDownFile
from mdutils.tools.Image import Image
from mdutils.tools.Link import Inline, Reference
from mdutils.tools.TextUtils import TextUtils

from ..log import log_item


def new_inline_link(link, text=None):
    """Creates a inline link in markdown format.

    :param link:
    :type link: str
    :param text: Text that is going to be displayed in the markdown file as a link.
    :type text: str
    :return: returns the link in markdown format ``'[ + text + '](' + link + ')'``. If text is not defined returns \
    ``'<' + link + '>'``.
    :rtype: str

    .. note::
        If param text is not provided, link param will be used instead.

    """
    if text is None:
        n_text = link
    else:
        n_text = text

    return Inline.new_link(link=link, text=n_text)


class MarkdownDocument:
    """This class give some basic methods that helps the creation of Markdown files while you are executing a python
    code.

    The ``__init__`` variables are:

    - **file_name:** it is the name of the Markdown file.
    - **textUtils:** it is an instance of TextUtils Class.
    - **title:** it is the title of the Markdown file. It is written with Setext-style.
    - **file_data_text:** contains all the file data that will be written on the markdown file.
    """

    def __init__(self, path: Path, metadata: dict = {}):
        """

        :param file_name: it is the name of the Markdown file.
        :type file_name: str
        """
        log_item('Creating', path)
        self.path = path
        self.file_name = str(path)  # TODO: change all to Path
        self.textUtils = TextUtils
        self.indent = ''
        self.file_data_text = ''
        self._table_titles = []
        self.reference = Reference()
        self.image = Image(reference=self.reference)
        metadata['generated'] = True
        self.write('---\n')
        for key, value in metadata.items():
            self.write(f'{key}: {value}\n')
        self.write('---\n')
        self.write_title(metadata)

    def write_title(self, metadata: dict = {}):
        if 'title' not in metadata:
            return
        if 'hide' in metadata and 'title' in metadata['hide']:
            return
        self.heading(1, metadata['title'])

    def create_md_file(self) -> MarkDownFile:
        file = MarkDownFile(self.file_name)
        file.rewrite_all_file(self.file_data_text)
        return file

    def read_md_file(self, file_name):
        """Reads a Markdown file and save it to global class `file_data_text`.

        :param file_name: Markdown file's name that has to be read.
        :type file_name: str
        :return: optionally returns the file data content.
        :rtype: str
        """
        file_data = MarkDownFile().read_file(file_name)
        self.___update_file_data(file_data)

        return file_data

    def heading(self, level: int, title: str, link: str = None):
        hdr = '#' * level
        if link:
            self.write(f'\n{self.indent}{hdr} [{title}]({link})\n\n')
        else:
            self.write(f'\n{self.indent}{hdr} {title}\n\n')

    def new_table(self, columns, rows, text):
        """This method takes a list of strings and creates a table.

            Using arguments ``columns`` and ``rows`` allows to create a table of *n* columns and *m* rows. The
            ``columns * rows`` operations has to correspond to the number of elements of ``text`` list argument.
            Moreover, ``argument`` allows to place the table wherever you want from the file.

        :param columns: this variable defines how many columns will have the table.
        :type columns: int
        :param rows: this variable defines how many rows will have the table.
        :type rows: int
        :param text: it is a list containing all the strings which will be placed in the table.
        :type text: list
        :return: can return the table created as a string.
        :rtype: str

        :Example:
        >>> from mdutils import MdUtils
        >>> md = MdUtils(file_name='Example')
        >>> text_list = ['List of Items', 'Description', 'Result', 'Item 1', 'Description of item 1',
                         '10', 'Item 2', 'Description of item 2', '0']
        >>> table = md.new_table(columns=3, rows=3, text=text_list)
        >>> print(repr(table))
        '\\n|List of Items|Description|Result|\\n| :---: | :---: | :---: |\\n|
        Item 1|Description of item 1|10|\\n|Item 2|Description of item 2|0|\\n'


            .. csv-table:: **Table result on Markdown**
               :header: "List of Items", "Description", "Results"

               "Item 1", "Description of Item 1", 10
               "Item 2", "Description of Item 2", 0

        """

        new_table = mdutils.tools.Table.Table()
        text_table = new_table.create_table(columns, rows, text)
        self.___update_file_data(text_table)

        return text_table

    def new_paragraph(self, text='', wrap_width=120):
        """Add a new paragraph to Markdown file. The text is saved to the global variable file_data_text.

        :param text: is a string containing the paragraph text. Optionally, the paragraph text is returned.
        :type text: str
        :param wrap_width: wraps text with designated width by number of characters.
                           By default, long words are not broken.
                           Use width of 0 to disable wrapping.
        :type wrap_width: int
        :return:  ``'\\n\\n' + text``. Not necessary to take it, if only has to be written to
                    the file.
        :rtype: str

        """

        if wrap_width > 0:
            text = fill(
                text,
                wrap_width,
                break_long_words=False,
                replace_whitespace=False,
                drop_whitespace=False,
                initial_indent=self.indent,
                subsequent_indent=self.indent,
            )

        self.___update_file_data('\n\n')
        self.___update_file_data(text)

        return self.file_data_text

    def new_line_no_wrap(self, text=''):
        self.new_line(text, wrap_width=0)

    def new_line(self, text='', wrap_width=120):
        """Add a new line to Markdown file. The text is saved to the global variable file_data_text.

        :param text: is a string containing the paragraph text. Optionally, the paragraph text is returned.
        :type text: str
        :param wrap_width: wraps text with designated width by number of characters.
                           By default, long words are not broken.
                           Use width of 0 to disable wrapping.
        :type wrap_width: int
        :return: return a string ``'\\n' + text``. Not necessary to take it, if only has to be written to the
                    file.
        :rtype: str
        """

        if text == '':
            self.file_data_text += '\n'
            return self.file_data_text

        if wrap_width > 0:
            text = fill(
                text,
                wrap_width,
                break_long_words=False,
                replace_whitespace=False,
                drop_whitespace=False,
                initial_indent='',
                subsequent_indent=self.indent,
            )
        else:
            text_unformatted = text
            text = ''
            for line in text_unformatted.splitlines():
                if text == '':
                    text += line.strip()
                else:
                    text += f'\n{self.indent}{line.strip()}'

        self.file_data_text += '\n'
        self.___update_file_data(text)

        return self.file_data_text

    def write(self, text='', wrap_width=120):
        """Write text in ``file_Data_text`` string.

        :param text: a text a string.
        :type text: str
        :param wrap_width: wraps text with designated width by number of characters.
                           By default, long words are not broken.
                           Use width of 0 to disable wrapping.
        :type wrap_width: int
        """

        if wrap_width > 0:
            text = fill(
                text,
                wrap_width,
                break_long_words=False,
                replace_whitespace=False,
                drop_whitespace=False,
                initial_indent=self.indent,
                subsequent_indent=self.indent,
            )

        self.___update_file_data(text)

        return text

    def insert_code(self, code, language=''):
        """This method allows to insert a peace of code on a markdown file.

        :param code: code string.
        :type code: str
        :param language: code language: python, c++, c#...
        :type language: str
        :return:
        :rtype: str
        """
        md_code = '\n\n' + self.textUtils.insert_code(code, language)
        self.___update_file_data(md_code)
        return md_code

    def should_add_indent(self):
        if len(self.indent) == 0:
            return False
        if len(self.file_data_text) == 0:
            return True
        return self.file_data_text[-1] == '\n'

    def ___update_file_data(self, file_data):
        if self.should_add_indent():
            self.file_data_text += self.indent

        self.file_data_text += file_data


if __name__ == '__main__':
    import doctest

    doctest.testmod()
