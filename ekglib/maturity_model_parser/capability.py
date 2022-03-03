import textwrap
from pathlib import Path

from rdflib import RDFS, DCTERMS
from rdflib.term import Node

from .File import makedirs, File
from .markdown_document import MarkdownDocument
from .pages_yaml import PagesYaml
from ..namespace import MATURIY_MODEL


class MaturityModelCapability:
    from .capability_area import MaturityModelCapabilityArea
    class_label: str = "Capability"
    class_label_plural: str = "Capabilities"
    class_iri = MATURIY_MODEL.Capability

    def __init__(self, area: MaturityModelCapabilityArea, capability_node: Node, mkdocs: bool):
        self.graph = area.graph
        self.area = area
        self.capability_node = capability_node
        self.mkdocs = mkdocs

        self.name = self.graph.name_for(self.capability_node, self.class_label)
        self.local_name = self.graph.local_name_for(self.capability_node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(self.capability_node, self.class_label)
        self.full_dir = self.area.full_dir / self.local_type_name / self.local_name
        self.md_file = None
        makedirs(self.full_dir, self.class_label)

    def generate_markdown(self):
        self.generate_link_from_area_to_capability()
        self.md_file = MarkdownDocument(path=self.full_dir / 'index.md', metadata={
            "title": self.name
        })
        self.generate_summary()
        self.md_file.create_md_file()

    def generate_link_from_area_to_capability(self):
        link = Path('.') / self.local_type_name / self.local_name / 'index.md'
        self.area.md_file.new_line('- ' + self.area.md_file.new_inline_link(
            link=str(link), text=self.name
        ))

    def summaries(self):
        for rdfs_comment in self.graph.g.objects(self.capability_node, DCTERMS.description):
            yield str(rdfs_comment).strip()

    def generate_summary(self):
        # self.md_file.heading(2, "Summary")
        self.md_file.write(
            f"The capability _{self.name}_\n"
            f"is part of the capability area [_{self.area.name}_](../../index.md)\n"
            f"in the [_{self.area.pillar.name}_](../../index.md)."
        )
        self.md_file.write("\n")
        for summary in self.summaries():
            self.md_file.write(summary, wrap_width=0)

    @classmethod
    def generate_index_md(cls, area: MaturityModelCapabilityArea):
        graph = area.graph
        type_name = graph.local_type_name_for_type(cls.class_iri, cls.class_label)
        root = area.full_dir / type_name
        makedirs(root, cls.class_label_plural)
        md_file = MarkdownDocument(path=root / 'index.md', metadata={
            "title": f"{area.name} --- {cls.class_label_plural}"
        })
        md_file.write(
            f'An overview of all the capabilities in the area _{area.name}_:\n\n'
        )
        for capability in area.capabilities():
            md_file.heading(2, f"[{capability.name}](./{capability.local_name}/)")
            for summary in capability.summaries():
                md_file.write(str(summary).strip(), wrap_width=0)
                md_file.write("\n\n")

        md_file.create_md_file()

    @classmethod
    def generate_pages_yaml(cls, area: MaturityModelCapabilityArea):
        graph = area.graph
        type_name = graph.local_type_name_for_type(cls.class_iri, cls.class_label)
        root = area.full_dir / type_name
        makedirs(root, cls.class_label_plural)
        pages_yaml = PagesYaml(root=root, title=cls.class_label_plural)
        for capability in area.capabilities():
            pages_yaml.add(f"{capability.name}: {capability.local_name}")
        pages_yaml.add('...')
        pages_yaml.write()
