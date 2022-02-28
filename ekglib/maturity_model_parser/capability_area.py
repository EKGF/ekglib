from pathlib import Path
from typing import Optional

from mdutils import MdUtils
from rdflib import RDFS
from rdflib.term import Node

from ..log import log_item
from ..namespace import MATURIY_MODEL
from .graph import MaturityModelGraph
from .File import md_file, makedirs
from .pillar import MaturityModelPillar


class MaturityModelCapabilityArea:
    class_label: str = "Capability Area"
    graph: MaturityModelGraph
    pillar: MaturityModelPillar
    area_node: Node
    mkdocs: bool
    md_file: Optional[MdUtils] = None

    def __init__(self, pillar: MaturityModelPillar, area_node: Node, mkdocs: bool):
        self.graph = pillar.graph
        self.pillar = pillar
        self.area_node = area_node
        self.mkdocs = mkdocs

        self.name = self.graph.name_for(self.area_node, self.class_label)
        self.local_name = self.graph.local_name_for(self.area_node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(self.area_node, self.class_label)
        self.full_dir = self.pillar.full_dir / self.local_type_name / self.local_name
        self.full_path = self.full_dir / 'index.md'
        makedirs(self.full_dir, self.class_label)

    def generate_markdown(self):
        self.generate_link_from_pillar_to_capability_area()

        self.md_file = md_file(path=self.full_path, title=self.name, mkdocs=self.mkdocs)
        self.summary()
        self.md_file.new_header(level=2, title="Capabilities", add_table_of_contents='n')
        self.capabilities()
        self.md_file.create_md_file()

    def summary(self):
        self.md_file.new_header(level=2, title="Summary", add_table_of_contents='n')
        self.md_file.new_paragraph(
            f"The capability area _{self.name}_ is "
            f"in the [_{self.pillar.name}_](../../index.md).\n"
        )
        self.md_file.write("\n")
        for rdfs_comment in self.graph.g.objects(self.area_node, RDFS.comment):
            self.md_file.write(str(rdfs_comment).strip(), wrap_width=0)

    def generate_link_from_pillar_to_capability_area(self):
        link = Path('.') / self.local_type_name / self.local_name / 'index.md'
        self.pillar.md_file.new_line('- ' + self.pillar.md_file.new_inline_link(
            link=str(link), text=self.name
        ))

    def capabilities(self):
        from .capability import MaturityModelCapability
        log_item("Searching for", MATURIY_MODEL.inArea)
        for capability_node in self.graph.g.subjects(MATURIY_MODEL.inArea, self.area_node):
            MaturityModelCapability(self, capability_node, self.mkdocs).generate_markdown()