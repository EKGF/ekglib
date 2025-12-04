from __future__ import annotations

from os import getcwd
from os.path import relpath
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

from rdflib.term import Node

from ekglib.maturity_model_parser.pages_yaml import PagesYaml

from ..log.various import log_item
from ..namespace import MATURITY_MODEL
from .config import Config
from .File import makedirs
from .markdown_document import MarkdownDocument

if TYPE_CHECKING:
    from .capability import MaturityModelCapability


class MaturityModelCapabilityArea:
    from .pillar import MaturityModelPillar

    class_label: str = 'Capability Area'
    class_label_plural: str = 'Capability Areas'
    class_iri = MATURITY_MODEL.CapabilityArea

    def __init__(
        self,
        pillar: MaturityModelPillar,
        area_node: Node,
        pillar_fragments_dir: Path,
        config: Config,
    ):
        self.md_file: MarkdownDocument | None = None
        self.graph = pillar.graph
        self.pillar = pillar
        self.node = area_node
        self.config = config
        self._capabilities: list[Any] = list()

        self.name = self.graph.name_for(self.node, self.class_label)
        self.local_name = self.graph.local_name_for(self.node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(
            self.node, self.class_label
        )
        self.description = self.graph.description_for(self.node, '')
        # log_item("Area Description", self.description)
        self.full_dir = self.pillar.full_dir / self.local_name
        self.full_path = self.full_dir / 'index.md'
        self.fragments_dir = pillar_fragments_dir / self.local_name
        log_item(f'{self.class_label} Fragments', relpath(self.fragments_dir, getcwd()))
        makedirs(self.full_dir, self.class_label)

    def generate_markdown(self) -> None:
        self.generate_link_from_pillar_to_capability_area()
        self.generate_pages_yaml()
        self.generate_index_md()
        assert self.md_file is not None
        self.generate_summary(self.md_file)
        self.generate_capabilities()
        self.md_file.create_md_file()

    def generate_index_md(self) -> None:
        self.md_file = MarkdownDocument(
            path=self.full_path,
            metadata={'title': f'{self.class_label} &mdash; {self.name}'},
        )

    def generate_pages_yaml(self) -> None:
        """Generate the .pages.yaml file for the root directory of a capability area"""
        makedirs(self.full_dir, self.class_label_plural)
        pages_yaml = PagesYaml(root=self.full_dir, title=self.name)
        pages_yaml.add('...')
        for capability in self.capabilities():
            pages_yaml.add(f'{capability.name}: {capability.local_name}')
        pages_yaml.write()

    def generate_summary(self, md_file: MarkdownDocument) -> None:
        # self.md_file.heading(2, "Summary")
        md_file.new_line(
            f'_{self.name}_ is a {self.class_label} that is part of '
            f'the [_{self.pillar.name}_](../../index.md).<br/>',
            wrap_width=0,
        )
        self.generate_summary_short(md_file)

    def generate_summary_short(self, md_file: MarkdownDocument) -> None:
        self.graph.write_tag_line(md_file, self.node)
        self.graph.write_description(md_file, self.node)

    def generate_link_from_pillar_to_capability_area(self) -> None:
        assert self.pillar.md_file is not None
        link = Path('.') / self.local_name / 'index.md'
        self.pillar.md_file.new_line(f'- [{self.name}]({link})')

    def capabiliy_nodes_unsorted(self) -> Generator[Node, None, None]:
        for capability_node in self.graph.g.subjects(MATURITY_MODEL.inArea, self.node):
            yield capability_node

    def sort_key(self, element: Node) -> str:
        for sort_key_node in self.graph.g.objects(element, MATURITY_MODEL.sortKey):
            # log_item("Sort key of", f"{sort_key_node} -> {element}")
            return str(sort_key_node)
        sort_key_str = str(element)
        log_item('No sort key for', element)
        return sort_key_str

    def capability_nodes(self) -> list[Node]:
        nodes = list(self.capabiliy_nodes_unsorted())
        nodes.sort(key=self.sort_key)
        return nodes

    def capabilities_non_cached(
        self,
    ) -> Generator['MaturityModelCapability', None, None]:
        from .capability import MaturityModelCapability

        for capability_node in self.capability_nodes():
            yield MaturityModelCapability(
                self, capability_node, self.fragments_dir, self.config
            )

    def capabilities(self) -> list['MaturityModelCapability']:
        if len(self._capabilities) == 0:
            self._capabilities = list(self.capabilities_non_cached())
        return self._capabilities

    def generate_capabilities(self) -> None:
        assert self.md_file is not None
        from .capability import MaturityModelCapability

        self.md_file.heading(2, MaturityModelCapability.class_label_plural)
        # MaturityModelCapability.generate_index_md(self)
        for capability in self.capabilities():
            capability.generate_markdown()
            capability.generate_markdown()
