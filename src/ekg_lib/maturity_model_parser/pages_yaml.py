from __future__ import annotations

from pathlib import Path

from ekg_lib import log_item

from .File import File


class PagesYaml:
    def __init__(self, root: Path, title: str):
        self.root = root
        self.title = title
        self.nav = ['index.md']

    def add(self, item: str) -> None:
        self.nav.append(item)

    def write(self) -> None:
        file = File(False, self.root / '.pages.yaml')
        log_item('pages.yaml', file.path)
        data = f'title: {self.title}\nnav:'
        for item in self.nav:
            data += f'\n  - {item}'
        # log_item("pages.yaml", data)
        file.rewrite_all_file(data)
        file.rewrite_all_file(data)
