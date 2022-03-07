from rdflib.term import Node

from rdflib.term import Node

from .File import makedirs, copy_fragment
from .config import Config
from .graph import MaturityModelGraph
from .markdown_document import MarkdownDocument


class MaturityModelPillar:
    class_label: str = "Pillar"
    class_label_plural: str = "Pillars"

    def __init__(self, graph: MaturityModelGraph, model_node: Node, pillar_node: Node, config: Config):
        self.md_file = None
        self.graph = graph
        self.model_node = model_node
        self.pillar_node = pillar_node
        self.config = config

        self.name = self.graph.name_for(self.pillar_node, self.class_label)
        self.local_name = self.graph.local_name_for(self.pillar_node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(self.pillar_node, self.class_label)
        self.full_dir = self.config.output_root / self.local_type_name / self.local_name
        self.fragments_dir = self.config.fragments_root / self.local_type_name / self.local_name
        self._capability_areas = list()
        makedirs(self.full_dir, self.class_label)

    def generate(self):
        self.md_file = MarkdownDocument(path=self.full_dir / 'index.md', metadata={
            "title": self.name
        })
        self.generate_capability_areas()
        self.copy_fragments()
        self.md_file.create_md_file()

    def copy_fragments(self):
        copy_fragment(self.md_file, self.fragments_dir / 'background-and-intro.md', self.config)

    def capability_area_nodes(self):
        return self.graph.capability_areas_of_pillar(self.pillar_node)

    def capability_areas_not_cached(self):
        from .capability_area import MaturityModelCapabilityArea
        for area in self.capability_area_nodes():
            yield MaturityModelCapabilityArea(self, area, self.fragments_dir, self.config)

    def capability_areas(self):
        if len(self._capability_areas) == 0:
            self._capability_areas = list(self.capability_areas_not_cached())
        return self._capability_areas

    def generate_capability_areas(self):
        from .capability_area import MaturityModelCapabilityArea
        self.md_file.heading(2, MaturityModelCapabilityArea.class_label_plural)
        MaturityModelCapabilityArea.generate_index_md(self)
        MaturityModelCapabilityArea.generate_pages_yaml(self)
        for area in self.capability_areas():
            area.generate_markdown()

    def number_of_capabilities(self) -> int:
        count = 0
        for area in self.capability_areas():
            count += len(area.capabilities())
        return count
