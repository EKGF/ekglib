import os
import textwrap
from pathlib import Path
from typing import Optional

from mdutils import MdUtils
from rdflib.term import Node

from .markdown_document import MarkdownDocument
from ..log import log_item
from .graph import MaturityModelGraph
from .File import makedirs, File


class MaturityModelPillar:
    class_label: str = "Pillar"
    class_label_plural: str = "Pillars"

    def __init__(self, graph: MaturityModelGraph, model_node: Node, pillar_node: Node, mkdocs: bool, output_root: Path):
        self.md_file = None
        self.graph = graph
        self.model_node = model_node
        self.pillar_node = pillar_node
        self.mkdocs = mkdocs
        self.output_root = output_root

        self.name = self.graph.name_for(self.pillar_node, self.class_label)
        self.local_name = self.graph.local_name_for(self.pillar_node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(self.pillar_node, self.class_label)
        self.full_dir = self.output_root / self.local_type_name / self.local_name
        self._capability_areas = list()
        makedirs(self.full_dir, self.class_label)

    def generate(self):
        self.md_file = MarkdownDocument(path=self.full_dir / 'index.md', metadata={
            "title": self.name
        })
        self.md_file.heading(2, "Capability Areas")
        self.generate_capability_areas()
        for fragment in self.graph.fragment_background_and_intro(self.pillar_node):
            self.copy_fragment(from_path=Path(str(fragment)), to_path=self.full_dir)
            self.md_file.write(
                "\n\n{% include-markdown \""
                f"{fragment}"
                "\" heading-offset=1 %}",
                wrap_width=0
            )
        self.md_file.create_md_file()

    def copy_fragment(self, from_path: Path, to_path: Path):
        log_item("Copying fragment", from_path)
        to_path2 = to_path / from_path.name
        log_item("to", to_path2)
        log_item("Current directory", os.getcwd())
        File.copy(self.mkdocs, from_path=from_path, to_path=to_path2)

    def capability_area_nodes(self):
        return self.graph.capability_areas_of_pillar(self.pillar_node)

    def capability_areas_not_cached(self):
        from .capability_area import MaturityModelCapabilityArea
        for area in self.capability_area_nodes():
            yield MaturityModelCapabilityArea(self, area, self.mkdocs)

    def capability_areas(self):
        if len(self._capability_areas) == 0:
            self._capability_areas = list(self.capability_areas_not_cached())
        return self._capability_areas

    def generate_capability_areas(self):
        from .capability_area import MaturityModelCapabilityArea
        MaturityModelCapabilityArea.generate_index_md(self)
        MaturityModelCapabilityArea.generate_pages_yaml(self)
        for area in self.capability_areas():
            area.generate_markdown()

