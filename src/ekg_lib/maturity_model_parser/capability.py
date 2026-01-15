from __future__ import annotations

from os import getcwd
from os.path import relpath
from pathlib import Path

from rdflib.term import Node

from ekg_lib import log_item

from ..namespace import MATURITY_MODEL
from .config import Config
from .File import copy_fragment, makedirs
from .markdown_document import MarkdownDocument
from .pages_yaml import PagesYaml


class MaturityModelCapability:
    from .capability_area import MaturityModelCapabilityArea

    class_label: str = 'Capability'
    class_label_plural: str = 'Capabilities'
    class_iri = MATURITY_MODEL.Capability

    def __init__(
        self,
        area: MaturityModelCapabilityArea,
        capability_node: Node,
        capability_area_fragments_dir: Path,
        config: Config,
    ):
        self.graph = area.graph
        self.area = area
        self.node = capability_node
        self.config = config

        self.name = self.graph.name_for(self.node, self.class_label)
        self.number = self.graph.capability_number_for(self.node, self.class_label)
        self.local_name = self.graph.local_name_for(self.node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(
            self.node, self.class_label
        )
        self.tag_line = self.graph.tag_line_for(self.node)
        self.full_dir = self.area.full_dir / self.local_name
        self.fragments_dir = capability_area_fragments_dir / self.local_name
        log_item(f'{self.class_label} Fragments', relpath(self.fragments_dir, getcwd()))
        self.md_file: MarkdownDocument | None = None
        makedirs(self.full_dir, self.class_label)

    def generate_markdown(self) -> None:
        self.md_file = MarkdownDocument(
            path=self.full_dir / 'index.md',
            metadata={'title': f'{self.number}. {self.name}'},
        )
        self.generate_summary()
        self.copy_fragments()
        assert self.md_file is not None
        self.md_file.create_md_file()

    def generate_link_from_area_to_capability(self) -> None:
        assert self.area.md_file is not None
        link = Path('.') / self.local_name / 'index.md'
        self.area.md_file.new_line(f'- [{self.name}]({link})')

    def generate_summary(self) -> None:
        assert self.md_file is not None
        # self.md_file.heading(2, "Summary")
        indent_prefix = '    '
        self.graph.write_tag_line(self.md_file, self.node)
        self.md_file.indent = indent_prefix
        self.md_file.new_line('\n=== "Summary"\n\n')
        self.md_file.new_line(
            f'The capability _{self.name}_ ({self.number})\n'
            f'is part of the capability area [_{self.area.name}_](../../index.md)\n'
            f'in the [_{self.area.pillar.name}_](../../index.md).',
            wrap_width=0,
        )
        self.md_file.new_line()
        self.graph.write_tag_line(self.md_file, self.node)
        self.md_file.new_line()
        self.graph.write_description(self.md_file, self.node)

    def copy_fragments(self) -> None:
        assert self.md_file is not None
        indent_prefix = '    '
        self.md_file.new_line('\n\n=== "Intro"')
        copy_fragment(
            self.md_file,
            self.fragments_dir / 'background-and-intro.md',
            self.config,
            indent_prefix,
        )
        self.md_file.new_line('\n\n=== "Dimensions"')
        copy_fragment(
            self.md_file,
            self.fragments_dir / 'dimensions.md',
            self.config,
            indent_prefix,
        )
        self.md_file.new_line('\n\n=== "Levels"')
        copy_fragment(
            self.md_file, self.fragments_dir / 'levels.md', self.config, indent_prefix
        )
        self.md_file.new_line('\n\n=== "Value"')
        copy_fragment(
            self.md_file, self.fragments_dir / 'value.md', self.config, indent_prefix
        )
        self.md_file.new_line('\n\n=== "Traditional Approach"')
        copy_fragment(
            self.md_file,
            self.fragments_dir / 'traditional-approach.md',
            self.config,
            indent_prefix,
        )
        self.md_file.new_line('\n\n=== "EKG Approach"')
        copy_fragment(
            self.md_file,
            self.fragments_dir / 'ekg-approach.md',
            self.config,
            indent_prefix,
        )
        self.md_file.new_line('\n\n=== "Use cases"')
        copy_fragment(
            self.md_file,
            self.fragments_dir / 'use-cases.md',
            self.config,
            indent_prefix,
        )

    # @classmethod
    # def generate_index_md(cls, area: MaturityModelCapabilityArea):
    #     graph = area.graph
    #     type_name = graph.local_type_name_for_type(cls.class_iri, cls.class_label)
    #     root = area.full_dir / type_name
    #     makedirs(root, cls.class_label_plural)
    #     md_file = MarkdownDocument(path=root / 'index.md', metadata={
    #         "title": f"{area.name} --- {cls.class_label_plural}"
    #     })
    #     md_file.write(
    #         f'An overview of all the capabilities in the area _{area.name}_:\n\n'
    #     )
    #     for capability in area.capabilities():
    #         md_file.heading(2, f"{capability.number}. [{capability.name}](./{capability.local_name}/)")
    #         graph.write_tag_line(md_file, capability, '')
    #         graph.write_description(md_file, capability, '')
    #
    #     md_file.create_md_file()

    @classmethod
    def generate_pages_yaml(cls, area: 'MaturityModelCapabilityArea') -> None:
        root = area.full_dir
        makedirs(root, cls.class_label_plural)
        pages_yaml = PagesYaml(root=root, title=cls.class_label_plural)
        for capability in area.capabilities():
            pages_yaml.add(f'{capability.name} - capability: {capability.local_name}')
        pages_yaml.add('...')
        pages_yaml.write()
