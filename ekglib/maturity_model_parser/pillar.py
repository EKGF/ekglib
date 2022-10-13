from __future__ import annotations

from os.path import relpath

from rdflib.term import Node

from .File import makedirs, copy_fragment
from .config import Config
from .graph import MaturityModelGraph
from .markdown_document import MarkdownDocument
from .pages_yaml import PagesYaml
from ..namespace import MATURITY_MODEL
from ..log import log_item


class MaturityModelPillar:

    from .model import MaturityModel

    class_iri: Node = MATURITY_MODEL.Pillar
    class_label: str = "Pillar"
    class_label_plural: str = "Pillars"

    def __init__(self, graph: MaturityModelGraph, model_node: Node, pillar_node: Node, config: Config):
        self.md_file = None
        self.graph = graph
        self.model_node = model_node
        self.node = pillar_node
        self.config = config

        self.name = self.graph.name_for(self.node, self.class_label)
        self.local_name = self.graph.local_name_for(self.node, self.class_label)

        self.pillars_root = MaturityModelPillar.pillars_root(graph=graph, config=config)
        log_item(f"{self.name}'s root", self.pillars_root)

        self.local_type_name = self.graph.local_type_name_for(self.node, self.class_label)
        self.full_dir = self.pillars_root / self.local_name
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
        return self.graph.capability_areas_of_pillar(self.node)

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

    @staticmethod
    def generate_pillars(model: MaturityModel):
        for pillar in model.pillars():
            pillar.generate()

    @staticmethod
    def pillars_root(graph: MaturityModelGraph, config: Config):
        if config.pillar_dir_name.is_none:
            pillar_type_name = graph.local_type_name_for_type(
                MaturityModelPillar.class_iri, MaturityModelPillar.class_label
            )
        else:
            pillar_type_name = config.pillar_dir_name.expect("")
        return config.output_root / pillar_type_name

    @staticmethod
    def generate_pillars_pages_yaml(model: MaturityModel):
        pages_yaml = PagesYaml(root=model.pillars_root, title="Pillars")
        pages_yaml.add('...')
        pages_yaml.write()

    @staticmethod
    def generate_index_md(model: MaturityModel):
        pillars_root = model.pillars_root
        index_md = pillars_root / 'index.md'
        model.md_file = MarkdownDocument(path=index_md, metadata={
            'title': 'Pillars',
            'hide': [
                'navigation',
                'toc',
                'title'
            ]
        })
        card_indent_1 = "    "
        card_indent_2 = "         "
        icon = ":orange_book:"
        arrow = ":octicons-arrow-right-24:"
        icon_style = "{ .lg .middle }"
        md_file = model.md_file
        for pillar in model.pillars():
            md_file.new_line(f'\n=== "{pillar.name}"\n')
            md_file.indent = card_indent_1
            md_file.new_line('<div class="grid cards annotate" markdown>')
            for index, area in enumerate(pillar.capability_areas()):
                index2 = index + 1
                capability_area_path = relpath(area.full_dir, pillars_root)
                md_file.indent = card_indent_1
                md_file.new_line('')
                md_file.new_line(f"- {icon}{icon_style} __[{area.name}]({capability_area_path}/index.md)__({index2})", wrap_width=0)
                md_file.indent = card_indent_2
                md_file.new_line('')
                md_file.new_line('------')
                md_file.new_line('')
                for capability in area.capabilities():
                    capability_path = relpath(capability.full_dir, pillars_root)
                    md_file.new_line(f"- [{capability.name}]({capability_path})", wrap_width=0)
                md_file.new_line('')
                if area.description is not None:
                    md_file.new_line('------')
                    md_file.new_line(area.description, wrap_width=0)
                md_file.new_line(f"[{arrow}{icon_style} Learn more]({capability_area_path}/index.md)\n", wrap_width=0)
            md_file.indent = card_indent_1
            md_file.new_line('</div>\n')
            for index, area in enumerate(pillar.capability_areas()):
                index2 = index + 1
                md_file.new_line(f"{index2}.  This is the Capability Area {area.name} in the {pillar.name}")

        md_file.create_md_file()
