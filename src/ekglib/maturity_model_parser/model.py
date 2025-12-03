from __future__ import annotations

from os.path import relpath
from pathlib import Path
from typing import Generator, Any, TYPE_CHECKING

from ekglib.maturity_model_parser.pages_yaml import PagesYaml
from rdflib.term import Node

from .File import makedirs
from .config import Config
from .graph import MaturityModelGraph
from .markdown_document import MarkdownDocument
from ..log.various import value_error, log_item
from ..namespace import MATURITY_MODEL

if TYPE_CHECKING:
    from .pillar import MaturityModelPillar


class MaturityModel:
    class_label: str = 'Model'
    class_label_plural: str = 'Models'

    def __init__(self, graph: MaturityModelGraph, model_node: Node, config: Config):
        log_item('Generating pages for', model_node)
        from .pillar import MaturityModelPillar

        self.md_file = None
        self.graph = graph
        self.model_node = model_node
        # self.model_node = graph.model_with_name(config.model_name)
        self.config = config

        self.name = self.graph.name_for(self.model_node, self.class_label)
        self.local_name = self.graph.local_name_for(self.model_node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(
            self.model_node, self.class_label
        )
        self.full_dir = self.config.output_root / self.local_type_name
        pillars_root_result = MaturityModelPillar.pillars_root(
            graph=graph, config=config
        )
        self.pillars_root: Path = pillars_root_result  # type: ignore[assignment]
        makedirs(self.full_dir, self.class_label)
        self._pillars: list[Any] = list()

    def sort_key(self, element):
        for sort_key in self.graph.g.objects(
            subject=element, predicate=MATURITY_MODEL.sortKey
        ):
            log_item('Sort key of', f'{sort_key} -> {element}')
            return str(sort_key)
        sort_key = str(element)
        log_item('No sort key for', element)
        return sort_key

    def pillar_nodes_unsorted(self):
        found = 0
        for pillar in self.graph.g.subjects(
            predicate=MATURITY_MODEL.pillarInModel, object=self.model_node
        ):
            log_item('Pillar', pillar)
            found += 1
            yield pillar
        if found == 0:
            raise value_error(f'Model has no pillars: <{self.model_node}>')

    def pillar_nodes(self):
        nodes = list(self.pillar_nodes_unsorted())
        nodes.sort(key=self.sort_key)
        return nodes

    def pillars_non_cached(self) -> Generator['MaturityModelPillar', Any, None]:
        from .pillar import MaturityModelPillar

        for pillar_node in self.pillar_nodes():
            yield MaturityModelPillar(
                graph=self.graph,
                model_node=self.model_node,
                pillar_node=pillar_node,
                config=self.config,
            )

    def pillars(self):
        if len(self._pillars) == 0:
            self._pillars = list(self.pillars_non_cached())
        return self._pillars

    def get_pillars_with_name(
        self, name: str
    ) -> Generator['MaturityModelPillar', Any, None]:
        for pillar in self.pillars():
            if pillar.name == name:
                yield pillar

    def generate(self):
        log_item('Generate model', self.model_node)
        self.generate_index_md()
        self.generate_pages_yaml()
        self.generate_pillars()
        self.generate_capabilities_overview_table()
        # self.generate_capabilities_overview()

    def generate_pillars(self):
        for pillar in self.pillars():
            pillar.generate()

    def generate_index_md(self):
        pillars_root = self.pillars_root
        index_md = pillars_root / 'index.md'
        self.md_file = MarkdownDocument(
            path=index_md,
            metadata={
                'title': 'Maturity Model',
                'hide': ['navigation', 'toc', 'title'],
            },
        )
        card_indent_1 = ' ' * 4
        card_indent_2 = ' ' * 8
        icon = ':orange_book:'
        arrow = ':octicons-arrow-right-24:'
        icon_style = '{ .lg .middle }'
        md_file = self.md_file
        for pillar in self.pillars():
            md_file.new_line(f'\n=== "{pillar.name}"\n')
            md_file.indent = card_indent_1
            md_file.new_line('<div class="grid cards annotate" markdown>')
            for index, area in enumerate(pillar.capability_areas()):
                index2 = index + 1
                capability_area_path = relpath(area.full_dir, pillars_root)
                md_file.indent = card_indent_1
                md_file.new_line()
                md_file.new_line_no_wrap(
                    f'- {icon}{icon_style} __[{area.name}]({capability_area_path}/index.md)__({index2})'
                )
                md_file.indent = card_indent_2
                md_file.new_line()
                md_file.new_line('------')
                md_file.new_line()
                for capability in area.capabilities():
                    capability_path = relpath(capability.full_dir, pillars_root)
                    md_file.new_line(
                        f'- [{capability.name}]({capability_path}/index.md)',
                        wrap_width=0,
                    )
                md_file.new_line()
                if area.description is not None:
                    md_file.new_line(area.description, wrap_width=0)
                md_file.new_line_no_wrap(
                    f'[{arrow}{icon_style} Learn more]({capability_area_path}/index.md)<br/><br/>\n'
                )
            md_file.indent = card_indent_1
            md_file.new_line('</div>\n')
            for index, area in enumerate(pillar.capability_areas()):
                index2 = index + 1
                md_file.new_line(
                    f'{index2}.  This is the Capability Area {area.name} in the {pillar.name}'
                )

        md_file.create_md_file()

    def generate_pages_yaml(self):
        """Generate the .pages.yaml file for the root directory where the pillars get published"""
        root = self.pillars_root
        log_item('Generate model pages.yaml', root)
        makedirs(root, self.class_label_plural)
        pages_yaml = PagesYaml(root=root, title='Maturity Model')
        for area in self.pillars():
            pages_yaml.add(f'{area.name}: {area.local_name}')
        pages_yaml.write()

    def generate_capabilities_overview_table(self):
        overview_md_path = self.config.docs_root / 'intro' / 'overview.md'
        makedirs(overview_md_path.parent, 'Overview')
        overview_md = MarkdownDocument(
            path=overview_md_path,
            metadata={'title': 'Overview', 'hide': ['navigation', 'toc']},
        )
        # '<table markdown class="md-typeset__table maturity-model-overview">\n<thead>\n<tr>\n'
        overview_md.write(
            'The taxonomy of pillars, capability areas, capabilities, and their measurable abilities or summaries.\n\n'
            '<table markdown width="100%">\n'
            '<thead>\n<tr>\n'
            '<th>Pillar</th>\n'
            '<th>Area</th>\n'
            '<th>&nbsp;</th>\n'
            '<th>Capability</th>\n'
            '<th>Measurable ability</th>\n'
            '</tr>\n</thead>\n<tbody>\n',
            wrap_width=0,
        )
        for pillar_index, pillar in enumerate(self.pillars()):
            pillar_url = f'/pillar/{pillar.local_name}'
            overview_md.write(
                '<tr>\n'
                '<td width="1%" colspan="5" style="text-align:left;vertical-align:top;">'
                f'<a href="{pillar_url}">{pillar.name}</a></td>\n'
                '</tr>\n',
                wrap_width=0,
            )
            areas = pillar.capability_areas()
            for area_index, area in enumerate(areas):
                capabilities = area.capabilities()
                area_url = f'{pillar_url}/{area.local_name}'
                if area_index == 0:
                    overview_md.write(
                        '<tr>\n'
                        f'<td width="1%" rowspan="{len(pillar.capability_areas()) + pillar.number_of_capabilities()}">'
                        '</td>\n',
                        wrap_width=0,
                    )
                else:
                    overview_md.write('<tr>\n', wrap_width=0)
                overview_md.write(
                    f'<td width="1%" colspan="4" style="text-align:left;vertical-align:top;">'
                    f'<a href="{area_url}">{area.name}</a></td>\n'
                    '</tr>\n',
                    wrap_width=0,
                )
                for capability_index, capability in enumerate(capabilities):
                    capability_url = f'{area_url}/{capability.local_name}'
                    tag_line = capability.tag_line
                    if tag_line is None:
                        tag_line = '... todo ...'
                    if capability_index == 0:
                        overview_md.write(
                            '<tr>\n'
                            f'<td width="1%" rowspan="{len(capabilities)}"></td>\n',
                            wrap_width=0,
                        )
                    else:
                        overview_md.write('<tr>\n', wrap_width=0)
                    overview_md.write(
                        f'<td width="1%">{capability.number}</td>\n'
                        f'<td width="20%"><a href="{capability_url}">{capability.name}</a></td>\n'
                        f'<td width="77%">{tag_line}</td>\n'
                        '</tr>\n',
                        wrap_width=0,
                    )
        overview_md.write('</tbody>\n</table>\n', wrap_width=0)
        overview_md.create_md_file()

    def generate_capabilities_overview(self):
        overview_md_path = self.config.docs_root / 'intro' / 'overview.md'
        makedirs(overview_md_path.parent, 'Overview')
        overview_md = MarkdownDocument(
            path=overview_md_path,
            metadata={'title': 'Overview', 'hide': ['navigation', 'toc']},
        )
        # "|Pillar|Area|&nbsp;|Capability|<div style=\"width:800px;background-color:blue;\">Measurable ability</div>|\n"
        overview_md.write(
            'The taxonomy of pillars, capability areas, capabilities, and their measurable abilities or summaries.\n\n'
            '|Pillar|Area|&nbsp;|Capability|Measurable ability|\n'
            '|------|----|------|----------|------------------|\n',
            wrap_width=0,
        )
        for pillar_index, pillar in enumerate(self.pillars()):
            pillar_url = f'/pillar/{pillar.local_name}'
            overview_md.write(
                f'|[{pillar.name}]({pillar_url}) {{ .foo }}| ~~ | ~~ | ~~ | ~~ |\n',
                wrap_width=0,
            )
            areas = pillar.capability_areas()
            for area_index, area in enumerate(areas):
                capabilities = area.capabilities()
                last_area = area_index == (len(areas) - 1)
                pillar_filler = '_ _' if last_area and len(capabilities) == 0 else '   '
                area_url = f'{pillar_url}/{area.local_name}'
                overview_md.write(
                    f'|{pillar_filler}|[{area.name}]({area_url}) {{ .foo }}| ~~ |~~ | ~~ |\n',
                    wrap_width=0,
                )
                for capability_index, capability in enumerate(capabilities):
                    last_capability = capability_index == (len(capabilities) - 1)
                    pillar_filler = '_ _' if last_area and last_capability else '   '
                    area_filler = '_ _' if last_capability else '   '
                    capability_url = f'{area_url}/{capability.local_name}'
                    tag_line = capability.tag_line
                    if tag_line is None:
                        tag_line = '... todo ...'
                    overview_md.write(
                        f'|{pillar_filler}|{area_filler}|{capability.number}|'
                        f'[{capability.name}]({capability_url})|{tag_line}|\n',
                        wrap_width=0,
                    )
        overview_md.create_md_file()
