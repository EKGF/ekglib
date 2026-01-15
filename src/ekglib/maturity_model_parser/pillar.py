from __future__ import annotations

from os import getcwd
from os.path import relpath
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

from rdflib.term import Node

from ekglib.maturity_model_parser.pages_yaml import PagesYaml

from ..log import log_item
from ..namespace import MATURITY_MODEL
from .config import Config
from .File import copy_fragment, makedirs
from .graph import MaturityModelGraph
from .markdown_document import MarkdownDocument

if TYPE_CHECKING:
    from .capability_area import MaturityModelCapabilityArea


class MaturityModelPillar:
    class_iri: Node = MATURITY_MODEL.Pillar
    class_label: str = 'Pillar'
    class_label_plural: str = 'Pillars'

    def __init__(
        self,
        graph: MaturityModelGraph,
        model_node: Node,
        pillar_node: Node,
        config: Config,
    ):
        self.md_file: MarkdownDocument | None = None
        self.graph = graph
        self.model_node = model_node
        self.node = pillar_node
        self.config = config

        self.name = self.graph.name_for(self.node, self.class_label)
        self.local_name = self.graph.local_name_for(self.node, self.class_label)

        pillars_root_result = MaturityModelPillar.pillars_root(
            graph=graph, config=config
        )
        # Store result in instance attribute (shadowing the staticmethod name)
        object.__setattr__(self, 'pillars_root', pillars_root_result)
        self.local_type_name = self.graph.local_type_name_for(
            self.node, self.class_label
        )
        self.full_dir: Path = self.pillars_root / self.local_name  # type: ignore[operator]
        self.fragments_dir = (
            self.config.fragments_root / self.local_type_name / self.local_name
        )
        log_item(f'{self.class_label} Fragments', relpath(self.fragments_dir, getcwd()))
        self._capability_areas: list[Any] = list()
        makedirs(self.full_dir, self.class_label)

    def generate(self) -> None:
        self.generate_index_md()
        self.generate_pages_yaml()
        self.generate_capability_areas()
        self.copy_fragments()
        assert self.md_file is not None
        self.md_file.create_md_file()
        for area in self.capability_areas():
            area.generate_markdown()

    def generate_index_md(self) -> None:
        self.md_file = MarkdownDocument(
            path=self.full_dir / 'index.md', metadata={'title': self.name}
        )

    def generate_pages_yaml(self) -> None:
        """Generate the .pages.yaml file for the root directory of a pillar"""
        makedirs(self.full_dir, self.class_label_plural)
        pages_yaml = PagesYaml(root=self.full_dir, title=self.name)
        pages_yaml.add(
            '...'
        )  # for the background-and-intro.md entry but possibly others
        for area in self.capability_areas():
            pages_yaml.add(f'{area.name}: {area.local_name}')
        pages_yaml.write()

    def copy_fragments(self) -> None:
        assert self.md_file is not None
        copy_fragment(
            self.md_file,
            self.fragments_dir / 'background-and-intro.md',
            self.config,
            '',
        )

    def capability_area_nodes(self) -> Generator[Node, None, None]:
        for node in self.graph.capability_areas_of_pillar(self.node):
            yield node

    def capability_areas_not_cached(
        self,
    ) -> Generator['MaturityModelCapabilityArea', None, None]:
        from .capability_area import MaturityModelCapabilityArea

        for area in self.capability_area_nodes():
            yield MaturityModelCapabilityArea(
                self, area, self.fragments_dir, self.config
            )

    def capability_areas(self) -> list['MaturityModelCapabilityArea']:
        if len(self._capability_areas) == 0:
            self._capability_areas = list(self.capability_areas_not_cached())
        return self._capability_areas

    def generate_capability_areas(self) -> None:
        assert self.md_file is not None
        pillar_icons = {
            'business': ':material-briefcase-outline:',
            'organization': ':material-account-group-outline:',
            'data': ':material-database-outline:',
            'technology': ':material-cog-outline:',
        }
        icon = pillar_icons.get(self.local_name, ':material-cube-outline:')
        arrow = ':octicons-arrow-right-24:'
        icon_style = '{ .middle }'
        md_file = self.md_file
        md_file.new_line('<div class="grid cards" markdown>')
        for area in self.capability_areas():
            capability_area_path = relpath(area.full_dir, self.full_dir)
            md_file.new_line()
            md_file.new_line(
                f'- {icon}{icon_style} __[{area.name}]({capability_area_path}/index.md)__',
                wrap_width=0,
            )
            md_file.indent = '    '
            md_file.new_line()
            md_file.new_line('------')
            md_file.new_line()
            area.generate_summary_short(md_file)
            md_file.new_line()
            md_file.new_line()
            for capability in area.capabilities():
                md_file.write(
                    f'- [{capability.name}]({capability_area_path}/{capability.local_name}/index.md)\n',
                    wrap_width=0,
                )
            md_file.new_line()
            md_file.write(
                f'[{arrow}{icon_style} Learn more]({area.local_name}/index.md)\n',
                wrap_width=0,
            )
            md_file.indent = ''
        md_file.new_line()
        md_file.new_line('</div>')

    def number_of_capabilities(self) -> int:
        count = 0
        for area in self.capability_areas():
            count += len(area.capabilities())
        return count

    @staticmethod
    def pillars_root(graph: MaturityModelGraph, config: Config) -> Path:
        if config.pillar_dir_name.is_none:
            pillar_type_name = graph.local_type_name_for_type(
                MaturityModelPillar.class_iri, MaturityModelPillar.class_label
            )
        else:
            pillar_type_name = config.pillar_dir_name.expect('')
        return config.output_root / pillar_type_name
        return config.output_root / pillar_type_name
