from pathlib import Path
from typing import Optional

from mdutils import MdUtils
from rdflib.term import Node

from ..log import log_item
from .graph import MaturityModelGraph
from .File import md_file, makedirs


class MaturityModelPillar:
    class_label: str = "Pillar"
    graph: MaturityModelGraph
    pillar_node: Node
    mkdocs: bool
    output_root: Path
    md_file: Optional[MdUtils] = None

    def __init__(self, graph: MaturityModelGraph, model_node: Node, pillar_node: Node, mkdocs: bool, output_root: Path):
        self.graph = graph
        self.model_node = model_node
        self.pillar_node = pillar_node
        self.mkdocs = mkdocs
        self.output_root = output_root

        self.name = self.graph.name_for(self.pillar_node, self.class_label)
        self.local_name = self.graph.local_name_for(self.pillar_node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(self.pillar_node, self.class_label)
        self.full_dir = self.output_root / self.local_type_name / self.local_name
        self.full_path = self.full_dir / 'index.md'
        makedirs(self.full_dir, self.class_label)

    def generate(self):
        log_item("Generating", self.full_path)
        self.md_file = md_file(path=self.full_path, title=self.name, mkdocs=self.mkdocs)
        self.md_file.new_header(level=2, title="Capability Areas", add_table_of_contents='n')
        self.capability_areas()
        self.md_file.create_md_file()

    def capability_areas(self):
        from .capability_area import MaturityModelCapabilityArea
        for area in self.graph.capability_areas_of_pillar(self.pillar_node):
            MaturityModelCapabilityArea(self, area, self.mkdocs).generate_markdown()