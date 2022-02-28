from pathlib import Path
from typing import Optional

from mdutils import MdUtils
from rdflib import RDFS
from rdflib.term import Node

from .File import md_file, makedirs
from .graph import MaturityModelGraph


class MaturityModelCapability:
    from .capability_area import MaturityModelCapabilityArea
    class_label: str = "Capability"
    graph: MaturityModelGraph
    area: MaturityModelCapabilityArea
    capability_node: Node
    mkdocs: bool
    md_file: Optional[MdUtils]

    def __init__(self, area: MaturityModelCapabilityArea, capability_node: Node, mkdocs: bool):
        self.graph = area.graph
        self.area = area
        self.capability_node = capability_node
        self.mkdocs = mkdocs

        self.name = self.graph.name_for(self.capability_node, self.class_label)
        self.local_name = self.graph.local_name_for(self.capability_node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(self.capability_node, self.class_label)
        self.full_dir = self.area.full_dir / self.local_type_name / self.local_name
        self.full_path = self.full_dir / 'index.md'
        self.md_file = None
        makedirs(self.full_dir, self.class_label)

    def generate_markdown(self):
        self.generate_link_from_area_to_capability()
        self.md_file = md_file(path=self.full_path, title=self.name, mkdocs=self.mkdocs)
        self.summary()
        self.md_file.create_md_file()

    def generate_link_from_area_to_capability(self):
        link = Path('.') / self.local_type_name / self.local_name / 'index.md'
        self.area.md_file.new_line('- ' + self.area.md_file.new_inline_link(
            link=str(link), text=self.name
        ))

    def summary(self):
        self.md_file.new_header(level=2, title="Summary", add_table_of_contents='n')
        self.md_file.new_paragraph(
            f"The capability _{self.name}_\n"
            f"is part of the capability area [_{self.area.name}_](../../index.md)\n"
            f"in the [_{self.area.pillar.name}_](../../index.md)."
        )
        self.md_file.write("\n")
        for rdfs_comment in self.graph.g.objects(self.capability_node, RDFS.comment):
            self.md_file.write(str(rdfs_comment).strip(), wrap_width=0)
