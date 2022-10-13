from __future__ import annotations
from pathlib import Path

from .File import File


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
        data = f"title: {self.title}\nnav:"
        for item in self.nav:
            data += f"\n  - {item}"
        file.rewrite_all_file(data)
