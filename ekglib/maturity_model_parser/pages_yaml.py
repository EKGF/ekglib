import textwrap

from ekglib.maturity_model_parser.File import File


class PagesYaml:

    def __init__(self, root: Path, title: str):
        self.root = root
        self.title = title
        self.nav = [
            'index.md'
        ]

    def add(self, item: str):
        self.nav.append(item)

    def write(self):
        file = File(False, self.root / '.pages.yaml')
        file.rewrite_all_file(textwrap.dedent(f"""\
            title: {self.title}
            nav:
        """))

