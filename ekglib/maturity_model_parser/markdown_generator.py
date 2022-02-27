import os
import textwrap
from os import getcwd
from pathlib import Path
from typing import Optional, Iterable

import rdflib
from mdutils import MdUtils
from rdflib import Graph, OWL, URIRef, RDF, RDFS
from rdflib.term import Node

from ekglib import log_item
from .File import File
from .mdutil_mkdocs import MdUtils4MkDocs
from ..log.various import value_error
from ..namespace import MATURIY_MODEL

OWL._fail = False  # workaround for this issue: https://github.com/RDFLib/OWL-RL/issues/53


def md_file(path: Path, title: str, mkdocs: bool):
    log_item("Creating", path)
    if mkdocs:
        return MdUtils4MkDocs(file_name=str(path), title=title)
    else:
        return MdUtils(file_name=str(path), title=title)


def makedirs(path: Path, hint: str):
    log_item(f"{hint} Path", path)
    try:
        os.makedirs(path)
    except FileExistsError:
        return


class MaturityModelGraph:
    g: rdflib.Graph

    def __init__(self, g: Graph, lang: str):
        self.g = g
        self.lang = lang

    def __name_with_lang_for(self, subject_uri, lang: Optional[str], hint: str):
        for uri, value in self.g.preferredLabel(subject_uri, lang=lang):
            if isinstance(value, rdflib.term.Literal):
                log_item(f"{hint} Name", value.toPython())
                return value.toPython()
            log_item(f"{hint} Name", value)
            log_item("Unknown Value Type", type(value))
            return value.toPython()
        return None

    def name_for(self, subject_uri, hint: str) -> str:
        name = self.__name_with_lang_for(subject_uri, self.lang, hint)  # first ask language specific label
        if name is not None:
            return name
        name = self.__name_with_lang_for(subject_uri, None, hint)  # then get language independent label
        if name is not None:
            return name
        raise value_error(f"{hint} has no label: {subject_uri}")

    def local_name_for(self, subject_node: Node, hint: str) -> str:
        for local_name in self.g.objects(subject_node, MATURIY_MODEL.iriLocalName):
            log_item(f"{hint} Local Name", local_name)
            return str(local_name)
        raise value_error(f"{hint} has no iriLocalName: {subject_node}")

    def local_type_name_for(self, subject_node: Node, hint: str) -> str:
        type_node = self.get_type(subject_node)
        return self.local_type_name_for_type(type_node, hint)

    def local_type_name_for_type(self, type_node: Node, hint: str) -> str:
        for local_type_name in self.g.objects(type_node, MATURIY_MODEL.iriLocalTypeName):
            log_item(f"{hint} Local Type Name", local_type_name)
            return str(local_type_name)
        raise value_error(f"{hint} has no iriLocalTypeName: {type_node}")

    def get_type(self, subject_node):
        for node_type in self.g.objects(subject_node, RDF.type):
            if node_type in (OWL.Thing, OWL.NamedIndividual):
                continue
            return node_type

    def has_type(self, subject_uri, type_uri):
        return (subject_uri, RDF.type, type_uri) in self.g

    def has_type_capability_area(self, subject_iri):
        return self.has_type(subject_iri, MATURIY_MODEL.CapabilityArea)

    def subjects_of_type(self, type_uri: URIRef) -> Iterable[Node]:
        return self.g.subjects(RDF.type, type_uri)

    def capability_areas_of_pillar(self, pillar_uri):
        for in_pillar_thing in self.g.subjects(MATURIY_MODEL.inPillar, pillar_uri):
            if self.has_type_capability_area(in_pillar_thing):
                yield in_pillar_thing


class MaturityModelPillar:
    class_label: str = "Pillar"
    graph: MaturityModelGraph
    pillar_node: Node
    mkdocs: bool
    output_root: Path

    def __init__(self, graph: MaturityModelGraph, model_node: Node, pillar_node: Node, mkdocs: bool, output_root: Path):
        self.graph = graph
        self.model_node = model_node
        self.pillar_node = pillar_node
        self.mkdocs = mkdocs
        self.output_root = output_root

        self.name = self.graph.name_for(self.pillar_node, self.class_label)
        self.local_name = self.graph.local_name_for(self.pillar_node, self.class_label)
        self.local_type_name = self.graph.local_type_name_for(self.pillar_node, self.class_label)
        self.full_dir = self.output_root / self.local_type_name / self.local_name
        self.full_path = self.full_dir / 'index.md'
        self.md_file = None
        makedirs(self.full_dir, self.class_label)

    def generate_markdown(self):
        self.md_file = md_file(path=self.full_path, title=self.name, mkdocs=self.mkdocs)
        self.md_file.new_header(level=2, title="Capability Areas", add_table_of_contents='n')
        self.capability_areas()
        self.md_file.create_md_file()

    def capability_areas(self):
        for area in self.graph.capability_areas_of_pillar(self.pillar_node):
            MaturityModelCapabilityArea(self, area, self.mkdocs).generate_markdown()


class MaturityModelCapabilityArea:
    class_label: str = "Capability Area"
    graph: MaturityModelGraph
    pillar: MaturityModelPillar
    area_node: Node
    mkdocs: bool
    md_file: Optional[MdUtils]

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
        self.md_file = None
        makedirs(self.full_dir, self.class_label)

    def generate_markdown(self):
        self.generate_link_from_pillar_to_capability_area()

        self.md_file = md_file(path=self.full_path, title=self.name, mkdocs=self.mkdocs)
        self.summary()
        self.md_file.new_header(level=2, title="Capabilities", add_table_of_contents='n')
        self.capabilities()
        self.md_file.create_md_file()

    def summary(self):
        self.md_file.new_header(level=2, title="Summary",add_table_of_contents='n')
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
        log_item("Searching for", MATURIY_MODEL.inArea)
        for capability_node in self.graph.g.subjects(MATURIY_MODEL.inArea, self.area_node):
            MaturityModelCapability(self, capability_node, self.mkdocs).generate_markdown()


class MaturityModelCapability:
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
        self.md_file.new_header(level=2, title="Summary",add_table_of_contents='n')
        self.md_file.new_paragraph(
            f"The capability _{self.name}_\n"
            f"is part of the capability area [_{self.area.name}_](../../index.md)\n"
            f"in the [_{self.area.pillar.name}_](../../index.md)."
        )
        self.md_file.write("\n")
        for rdfs_comment in self.graph.g.objects(self.capability_node, RDFS.comment):
            self.md_file.write(str(rdfs_comment).strip(), wrap_width=0)


class MaturityModelMarkdownGenerator:
    """Checks each `capability.ttl` file in the given repository directory
        TODO: Create abstract interface and use that to implement other formats to generate
    """
    graph: MaturityModelGraph
    mkdocs: bool
    output_root: Path
    md_file: Optional[MdUtils]

    def __init__(self, graph: MaturityModelGraph, mkdocs: bool, output_root: Path):
        self.graph = graph
        self.mkdocs = mkdocs
        self.output_root = output_root

        self.local_type_name = self.graph.local_type_name_for_type(MATURIY_MODEL.Pillar,
                                                                   MaturityModelPillar.class_label)
        self.full_dir = self.output_root / self.local_type_name
        self.full_path = self.full_dir / 'index.md'
        self.md_file = None

    def generate(self):
        self.generate_pages_yaml()
        self.generate_index()
        self.generate_pillars()

    def generate_pages_yaml(self):
        pages_yaml = File(self.mkdocs, self.full_dir / '.pages.yaml')
        pages_yaml.rewrite_all_file(textwrap.dedent("""\
            title: Pillars
            nav:
              - index.md
              - ...
        """))

    def generate_index(self):
        self.md_file = md_file(path=self.full_path, title="Pillars", mkdocs=self.mkdocs)

        for model_uri, pillar_uri in self.graph.g.subject_objects(MATURIY_MODEL.hasPillar):
            pillar = MaturityModelPillar(self.graph, model_uri, pillar_uri, self.mkdocs, self.output_root)
            self.md_file.new_line(f"- [{pillar.name}]({Path(pillar.local_name) / 'index.md'})")

        self.md_file.create_md_file()

    def generate_pillars(self):
        log_item("Generating", "Pillars")
        log_item("Searching for", MATURIY_MODEL.hasPillar)

        for model_uri, pillar_uri in self.graph.g.subject_objects(MATURIY_MODEL.hasPillar):
            MaturityModelPillar(self.graph, model_uri, pillar_uri, self.mkdocs, self.output_root).generate_markdown()
