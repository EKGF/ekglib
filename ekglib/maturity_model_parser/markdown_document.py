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
from mdutils.tools.MDList import MDList, MDCheckbox
from mdutils.tools.TextUtils import TextUtils

from ..log import log_item


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
        log_item("Creating", path)
        self.path = path
        self.file_name = str(path) # TODO: change all to Path
        self.textUtils = TextUtils
        self.indent = ""
        self.file_data_text = ""
        self._table_titles = []
        self.reference = Reference()
        self.image = Image(reference=self.reference)
        metadata['generated'] = True
        self.write("---\n")
        for key, value in metadata.items():
            self.write(f"{key}: {value}\n")
        self.write("---\n")
        if 'title' in metadata:
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
        hdr = "#" * level
        if link:
            self.write(f"\n{self.indent}{hdr} [{title}]({link})\n\n")
        else:
            self.write(f"\n{self.indent}{hdr} {title}\n\n")

    def new_table(self, columns, rows, text, text_align='center', marker=''):
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
        :param text_align: allows to align all the cells to the ``'right'``, ``'left'`` or ``'center'``.
                            By default: ``'center'``.
        :type text_align: str
        :param marker: using ``create_marker`` method can place the table anywhere of the markdown file.
        :type marker: str
        :return: can return the table created as a string.
        :rtype: str

        :Example:
        >>> from mdutils import MdUtils
        >>> md = MdUtils(file_name='Example')
        >>> text_list = ['List of Items', 'Description', 'Result', 'Item 1', 'Description of item 1', '10', 'Item 2', 'Description of item 2', '0']
        >>> table = md.new_table(columns=3, rows=3, text=text_list, text_align='center')
        >>> print(repr(table))
        '\\n|List of Items|Description|Result|\\n| :---: | :---: | :---: |\\n|Item 1|Description of item 1|10|\\n|Item 2|Description of item 2|0|\\n'


            .. csv-table:: **Table result on Markdown**
               :header: "List of Items", "Description", "Results"

               "Item 1", "Description of Item 1", 10
               "Item 2", "Description of Item 2", 0

        """

        new_table = mdutils.tools.Table.Table()
        text_table = new_table.create_table(columns, rows, text, text_align)
        if marker:
            self.file_data_text = self.place_text_using_marker(text_table, marker)
        else:
            self.___update_file_data(text_table)

        return text_table

    def new_paragraph(self, text='', bold_italics_code='', color='black', align='', wrap_width=120):
        """Add a new paragraph to Markdown file. The text is saved to the global variable file_data_text.

        :param text: is a string containing the paragraph text. Optionally, the paragraph text is returned.
        :type text: str
        :param bold_italics_code: using ``'b'``: **bold**, ``'i'``: *italics* and ``'c'``: ``inline_code``.
        :type bold_italics_code: str
        :param color: Can change text color. For example: ``'red'``, ``'green'``, ``'orange'``...
        :type color: str
        :param align: Using this parameter you can align text.
        :type align: str
        :param wrap_width: wraps text with designated width by number of characters. By default, long words are not broken.
                           Use width of 0 to disable wrapping.
        :type wrap_width: int
        :return:  ``'\\n\\n' + text``. Not necessary to take it, if only has to be written to
                    the file.
        :rtype: str

        """

        if wrap_width > 0:
            text = fill(
                text, wrap_width,
                break_long_words=False,
                replace_whitespace=False,
                drop_whitespace=False,
                initial_indent=self.indent,
                subsequent_indent=self.indent
            )

        if bold_italics_code or color != 'black' or align:
            self.___update_file_data('\n\n' + self.textUtils.text_format(text, bold_italics_code, color, align))
        else:
            self.___update_file_data('\n\n' + text)

        return self.file_data_text

    def new_line(self, text='', bold_italics_code='', color='black', align='', wrap_width=120):
        """Add a new line to Markdown file. The text is saved to the global variable file_data_text.

        :param text: is a string containing the paragraph text. Optionally, the paragraph text is returned.
        :type text: str
        :param bold_italics_code: using ``'b'``: **bold**, ``'i'``: *italics* and ``'c'``: ``inline_code``...
        :type bold_italics_code: str
        :param color: Can change text color. For example: ``'red'``, ``'green'``, ``'orange'``...
        :type color: str
        :param align: Using this parameter you can align text. For example ``'right'``, ``'left'`` or ``'center'``.
        :type align: str
        :param wrap_width: wraps text with designated width by number of characters. By default, long words are not broken.
                           Use width of 0 to disable wrapping.
        :type wrap_width: int
        :return: return a string ``'\\n' + text``. Not necessary to take it, if only has to be written to the
                    file.
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
                subsequent_indent=self.indent
            )
        else:
            text_unformatted = text
            text = ""
            for line in text_unformatted.splitlines():
                line = f"{self.indent}{line}"
                if text == "":
                    text += line
                else:
                    text += f"\n{line}"

        if bold_italics_code or color != 'black' or align:
            self.___update_file_data('\n' + self.textUtils.text_format(text, bold_italics_code, color, align))
        else:
            self.___update_file_data(f'\n{text}')

        return self.file_data_text

    def write(self, text='', bold_italics_code='', color='black', align='', marker='', wrap_width=120):
        """Write text in ``file_Data_text`` string.

        :param text: a text a string.
        :type text: str
        :param bold_italics_code: using ``'b'``: **bold**, ``'i'``: *italics* and ``'c'``: ``inline_code``...
        :type bold_italics_code: str
        :param color: Can change text color. For example: ``'red'``, ``'green'``, ``'orange'``...
        :type color: str
        :param align: Using this parameter you can align text. For example ``'right'``, ``'left'`` or ``'center'``.
        :type align: str
        :param wrap_width: wraps text with designated width by number of characters. By default, long words are not broken.
                           Use width of 0 to disable wrapping.
        :type wrap_width: int
        :param marker: allows to replace a marker on some point of the file by the text.
        :type marker: str
        """

        if wrap_width > 0:
            text = fill(
                text,
                wrap_width,
                break_long_words=False,
                replace_whitespace=False,
                drop_whitespace=False,
                initial_indent=self.indent,
                subsequent_indent=self.indent
            )

        if bold_italics_code or color or align:
            new_text = self.textUtils.text_format(text, bold_italics_code, color, align)
        else:
            new_text = text

        if marker:
            self.file_data_text = self.place_text_using_marker(new_text, marker)
        else:
            self.___update_file_data(new_text)

        return new_text

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

    def create_marker(self, text_marker):
        """This will add a marker to ``file_data_text`` and returns the marker result in order to be used whenever
            you need.

            Markers allows to place them to the string data text and they can be replaced by a peace of text using
            ``place_text_using_marker`` method.

        :param text_marker: marker name.
        :type text_marker: str
        :return: return a marker of the following form: ``'##--[' + text_marker + ']--##'``
        :rtype: str
        """

        new_marker = '##--[' + text_marker + ']--##'
        self.___update_file_data(new_marker)
        return new_marker

    def place_text_using_marker(self, text, marker):
        """It replace a previous marker created with ``create_marker`` with a text string.

            This method is going to search for the ``marker`` argument, which has been created previously using
            ``create_marker`` method, in ``file_data_text`` string.

        :param text: the new string that will replace the marker.
        :type text: str
        :param marker: the marker that has to be replaced.
        :type marker: str
        :return: return a new file_data_text with the replace marker.
        :rtype: str
        """
        return self.file_data_text.replace(marker, text)

    def ___update_file_data(self, file_data):
        self.file_data_text += file_data

    def new_inline_link(self, link, text=None, bold_italics_code='', align=''):
        """Creates a inline link in markdown format.

        :param link:
        :type link: str
        :param text: Text that is going to be displayed in the markdown file as a link.
        :type text: str
        :param bold_italics_code: Using ``'b'``: **bold**, ``'i'``: *italics* and ``'c'``: ``inline_code``...
        :type bold_italics_code: str
        :param align: Using this parameter you can align text. For example ``'right'``, ``'left'`` or ``'center'``.
        :type align: str
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

        if bold_italics_code or align:
            n_text = self.textUtils.text_format(text=n_text, bold_italics_code=bold_italics_code, align=align)

        return Inline.new_link(link=link, text=n_text)

    @staticmethod
    def new_inline_image(text, path):
        """Add inline images in a markdown file. For example ``[MyImage](../MyImage.jpg)``.

        :param text: Text that is going to be displayed in the markdown file as a iamge.
        :type text: str
        :param path: Image's path / link.
        :type path: str
        :return: return the image in markdown format ``'![ + text + '](' + path + ')'``.
        :rtype: str

        """

        return Image.new_inline_image(text=text, path=path)

    def new_list(self, items: [str], marked_with: str = "-"):
        """Add unordered or ordered list in MarkDown file.

        :param items: Array of items for generating the list.
        :type items: [str]
        :param marked_with: By default has the value of ``'-'``, can be ``'+'``, ``'*'``. If you want to generate
         an ordered list then set to ``'1'``.
        :type marked_with: str
        :return:
        """
        mdlist = MDList(items, marked_with)
        self.___update_file_data('\n' + mdlist.get_md())

    def new_checkbox_list(self, items: [str], checked: bool = False):
        """Add checkbox list in MarkDown file.

        :param items: Array of items for generating the checkbox list.
        :type items: [str]
        :param checked: if you set this to ``True``. All checkbox will be checked. By default is ``False``.
        :type checked: bool
        :return:
        """

        mdcheckbox = MDCheckbox(items=items, checked=checked)
        self.___update_file_data('\n' + mdcheckbox.get_md())


if __name__ == "__main__":
    import doctest

    doctest.testmod()
