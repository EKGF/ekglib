import textwrap
from pathlib import Path
from typing import Optional

from mdutils import MdUtils
from rdflib.term import Node

from ..namespace import MATURIY_MODEL
from .graph import MaturityModelGraph
from .File import makedirs, md_file, File
from .pillar import MaturityModelPillar


class MaturityModel:
    class_label: str = "Model"
    graph: MaturityModelGraph
    model_node: Node
    mkdocs: bool
    output_root: Path
    md_file: Optional[MdUtils] = None

    def __init__(self, graph: MaturityModelGraph, model_name: str, mkdocs: bool, output_root: Path):
        self.graph = graph
        self.model_node = graph.model_with_name(model_name)
        self.mkdocs = mkdocs
        self.output_root = output_root

        self.name = self.graph.name_for(self.model_node, self.class_label)
        self.local_name = self.graph.local_name_for(self.model_node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(self.model_node, self.class_label)
        self.full_dir = self.output_root / self.local_type_name
        self.pillar_type_name = self.graph.local_type_name_for_type(MATURIY_MODEL.Pillar, MaturityModelPillar.class_label)
        self.pillars_root = self.output_root / self.pillar_type_name
        makedirs(self.full_dir, self.class_label)
        self.pillars = list(map(lambda pillar_node: MaturityModelPillar(
            graph=self.graph,
            model_node=self.model_node,
            pillar_node=pillar_node,
            mkdocs=mkdocs,
            output_root=output_root
        ), self.graph.pillars(self.model_node)))

    def generate(self):
        self.generate_pillars_pages_yaml()
        self.generate_pillars_index()
        self.generate_pillars()

    def generate_pillars_pages_yaml(self):
        pages_yaml = File(self.mkdocs, self.pillars_root / '.pages.yaml')
        pages_yaml.rewrite_all_file(textwrap.dedent("""\
            title: Pillars
            nav:
              - index.md
              - ...
        """))

    def generate_pillars_index(self):
        index_md = self.pillars_root / 'index.md'
        self.md_file = md_file(path=index_md, title="Pillars", mkdocs=self.mkdocs)

        for pillar in self.pillars:
            self.md_file.new_line(f"- [{pillar.name}]({Path(pillar.local_name) / 'index.md'})")

        self.md_file.create_md_file()

    def generate_pillars(self):
        for pillar in self.pillars:
            pillar.generate()
