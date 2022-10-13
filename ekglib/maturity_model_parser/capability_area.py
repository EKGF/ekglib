from __future__ import annotations
from pathlib import Path
from rdflib.term import Node

from .File import makedirs
from .config import Config
from .markdown_document import MarkdownDocument
from .pages_yaml import PagesYaml
from ..log.various import log_item
from ..namespace import MATURITY_MODEL


class MaturityModelCapabilityArea:

    from .pillar import MaturityModelPillar

    class_label: str = "Capability Area"
    class_label_plural: str = "Capability Areas"
    class_iri = MATURITY_MODEL.CapabilityArea

    def __init__(
            self,
            pillar: MaturityModelPillar,
            area_node: Node,
            pillar_fragments_dir: Path,
            config: Config
    ):
        self.md_file = None
        self.graph = pillar.graph
        self.pillar = pillar
        self.node = area_node
        self.config = config
        self._capabilities = list()

        self.name = self.graph.name_for(self.node, self.class_label)
        self.local_name = self.graph.local_name_for(self.node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(self.node, self.class_label)
        self.description = self.graph.description_for(self.node, '')
        log_item("Area Description", self.description)
        self.full_dir = self.pillar.full_dir / self.local_type_name / self.local_name
        self.full_path = self.full_dir / 'index.md'
        self.fragments_dir = pillar_fragments_dir / self.local_type_name / self.local_name
        makedirs(self.full_dir, self.class_label)

    def generate_markdown(self):
        self.generate_link_from_pillar_to_capability_area()
        self.md_file = MarkdownDocument(path=self.full_path, metadata={
            'title': self.name
        })
        self.generate_summary()
        self.generate_capabilities()
        self.md_file.create_md_file()

    def generate_summary(self):
        # self.md_file.heading(2, "Summary")
        self.md_file.write(
            f"The capability area _{self.name}_ is "
            f"in the [_{self.pillar.name}_](../../index.md).\n",
            wrap_width=0
        )
        self.generate_summary_short(self.md_file)

    def generate_summary_short(self, md_file: MarkdownDocument):
        self.graph.write_tag_line(md_file, self.node, '')
        self.graph.write_description(md_file, self.node, '')

    def generate_link_from_pillar_to_capability_area(self):
        link = Path('.') / self.local_type_name / self.local_name / 'index.md'
        self.pillar.md_file.new_line('- ' + self.pillar.md_file.new_inline_link(
            link=str(link), text=self.name
        ))

    def capabiliy_nodes_unsorted(self):
        for capability_node in self.graph.g.subjects(MATURITY_MODEL.inArea, self.node):
            yield capability_node

    def sort_key(self, element):
        for sort_key in self.graph.g.objects(element, MATURITY_MODEL.sortKey):
            log_item("Sort key of", f"{sort_key} -> {element}")
            return str(sort_key)
        sort_key = str(element)
        log_item("No sort key for", element)
        return sort_key

    def capability_nodes(self):
        nodes = list(self.capabiliy_nodes_unsorted())
        nodes.sort(key=self.sort_key)
        return nodes

    def capabilities_non_cached(self):
        from .capability import MaturityModelCapability
        for capability_node in self.capability_nodes():
            yield MaturityModelCapability(self, capability_node, self.fragments_dir, self.config)

    def capabilities(self):
        if len(self._capabilities) == 0:
            self._capabilities = list(self.capabilities_non_cached())
        return self._capabilities

    def generate_capabilities(self):
        from .capability import MaturityModelCapability
        self.md_file.heading(2, MaturityModelCapability.class_label_plural)
        MaturityModelCapability.generate_index_md(self)
        MaturityModelCapability.generate_pages_yaml(self)
        for capability in self.capabilities():
            capability.generate_markdown()

    @classmethod
    def generate_index_md(cls, pillar: MaturityModelPillar):
        graph = pillar.graph
        type_name = graph.local_type_name_for_type(cls.class_iri, cls.class_label)
        root = pillar.full_dir / type_name
        makedirs(root, cls.class_label_plural)
        md_file = MarkdownDocument(path=root / 'index.md', metadata={
            "title": f"{pillar.name} --- {cls.class_label_plural}"
        })
        for area in pillar.capability_areas():
            md_file.heading(2, area.name, area.local_name)
            area.generate_summary_short(md_file)
            md_file.write(f'\n\n[More info...]({area.local_name})\n\n')
        md_file.create_md_file()

    @classmethod
    def generate_pages_yaml(cls, pillar: MaturityModelPillar):
        graph = pillar.graph
        type_name = graph.local_type_name_for_type(cls.class_iri, cls.class_label)
        root = pillar.full_dir / type_name
        makedirs(root, cls.class_label_plural)
        pages_yaml = PagesYaml(root=root, title=cls.class_label_plural)
        for area in pillar.capability_areas():
            pages_yaml.add(f"{area.name}: {area.local_name}")
        pages_yaml.write()
