import textwrap
from pathlib import Path

from rdflib import DCTERMS
from rdflib.term import Node

from .File import makedirs, File
from .markdown_document import MarkdownDocument
from .pages_yaml import PagesYaml
from .pillar import MaturityModelPillar
from ..log.various import value_error, log_item
from ..namespace import MATURIY_MODEL


class MaturityModelCapabilityArea:
    class_label: str = "Capability Area"
    class_label_plural: str = "Capability Areas"
    class_iri = MATURIY_MODEL.CapabilityArea

    def __init__(self, pillar: MaturityModelPillar, area_node: Node, mkdocs: bool):
        self.md_file = None
        self.graph = pillar.graph
        self.pillar = pillar
        self.area_node = area_node
        self.mkdocs = mkdocs
        self._capabilities = list()

        self.name = self.graph.name_for(self.area_node, self.class_label)
        self.local_name = self.graph.local_name_for(self.area_node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(self.area_node, self.class_label)
        self.full_dir = self.pillar.full_dir / self.local_type_name / self.local_name
        self.full_path = self.full_dir / 'index.md'
        makedirs(self.full_dir, self.class_label)

    def generate_markdown(self):
        from .capability import MaturityModelCapability
        self.generate_link_from_pillar_to_capability_area()
        self.md_file = MarkdownDocument(path=self.full_path, metadata={
            'title': self.name
        })
        self.summary()
        self.md_file.heading(2, MaturityModelCapability.class_label_plural)
        self.generate_capabilities()
        self.md_file.create_md_file()

    def summary(self):
        # self.md_file.heading(2, "Summary")
        self.md_file.new_paragraph(
            f"The capability area _{self.name}_ is "
            f"in the [_{self.pillar.name}_](../../index.md).\n"
        )
        self.md_file.write("\n")
        for rdfs_comment in self.graph.g.objects(self.area_node, DCTERMS.description):
            self.md_file.write(str(rdfs_comment).strip(), wrap_width=0)

    def generate_link_from_pillar_to_capability_area(self):
        link = Path('.') / self.local_type_name / self.local_name / 'index.md'
        self.pillar.md_file.new_line('- ' + self.pillar.md_file.new_inline_link(
            link=str(link), text=self.name
        ))

    def capabiliy_nodes_unsorted(self):
        for capability_node in self.graph.g.subjects(MATURIY_MODEL.inArea, self.area_node):
            yield capability_node

    def sort_key(self, element):
        for sort_key in self.graph.g.objects(element, MATURIY_MODEL.sortKey):
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
            yield MaturityModelCapability(self, capability_node, self.mkdocs)

    def capabilities(self):
        if len(self._capabilities) == 0:
            self._capabilities = list(self.capabilities_non_cached())
        return self._capabilities

    def generate_capabilities(self):
        from .capability import MaturityModelCapability
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
