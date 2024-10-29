from __future__ import annotations

import textwrap
from os import getcwd
from os.path import relpath
from pathlib import Path
from typing import Optional, Iterable

import rdflib
from rdflib import Graph, RDF, OWL, URIRef, RDFS, DCTERMS, SKOS
from rdflib.term import Node, Literal

from .config import Config
from .markdown_document import MarkdownDocument
from ..log import log_item
from ..log.various import value_error, warning
from ..namespace import MATURITY_MODEL


def get_text_in_language(
    graph: Graph, lang: str, subject: Node, predicate: URIRef, indent_prefix: str
):
    default_value = None
    for value in graph.objects(subject, predicate):
        if not isinstance(value, rdflib.Literal):
            raise value_error(
                f'Found non-literal as value for {predicate} for subject {subject}'
            )
        literal: Literal = value
        literal_lang = literal.language
        if literal_lang == lang:
            return textwrap.indent(textwrap.dedent(str(literal)).strip(), indent_prefix)
        if literal_lang is None:
            default_value = literal
        if default_value is None and literal_lang == 'en':
            default_value = literal
    if default_value is None:
        return None
    return textwrap.indent(textwrap.dedent(str(default_value)).strip(), indent_prefix)


class MaturityModelGraph:
    g: rdflib.Graph

    def __init__(self, g: Graph, config: Config, verbose: bool, lang: str):
        self.g = g
        self.config = config
        self.verbose = verbose
        self.lang = lang
        self._models = list()

    def __name_with_lang_for(self, subject_uri, lang: Optional[str], hint: str):
        for uri, value in self.preferred_label(subject_uri, lang=lang):
            if isinstance(value, rdflib.term.Literal):
                log_item(f'{hint} Name', value.toPython())
                return value.toPython()
            log_item(f'{hint} Name', value)
            log_item('Unknown Value Type', type(value))
            return value.toPython()
        return None

    def preferred_label(
        self,
        subject,
        lang=None,
        default=None,
        label_properties=(SKOS.prefLabel, RDFS.label),
    ):
        """
        Find the preferred label for subject.

        This method has been copied (and modified) from rdflib 6.1.1 where
        it was called "preferredLabel()".
        Tt was deprecated in later versions of rdflib.

        By default, prefers skos:prefLabels over rdfs:labels. In case at least
        one prefLabel is found returns those, else returns labels. In case a
        language string (e.g., "en", "de" or even "" for no lang-tagged
        literals) is given, only such labels will be considered.

        Return a list of (labelProp, label) pairs, where labelProp is either
        skos:prefLabel or rdfs:label.
        """

        if default is None:
            default = []

        # set up the language filtering
        if lang is not None:
            if lang == '':  # we only want not language-tagged literals
                lang_filter = lambda l_: l_.language is None  # noqa
            else:
                lang_filter = lambda l_: l_.language == lang  # noqa
        else:  # we don't care about language tags
            lang_filter = lambda l_: True  # noqa

        for labelProp in label_properties:
            labels = list(
                filter(
                    lang_filter, self.g.objects(subject=subject, predicate=labelProp)
                )
            )
            if len(labels) == 0:
                continue
            else:
                return [(labelProp, l_) for l_ in labels]
        return default

    def name_for(self, subject_uri, hint: str) -> str:
        name = self.__name_with_lang_for(
            subject_uri, self.lang, hint
        )  # first ask language specific label
        if name is not None:
            return name
        name = self.__name_with_lang_for(
            subject_uri, None, hint
        )  # then get language independent label
        if name is not None:
            return name
        raise value_error(f'{hint} has no label: {subject_uri}')

    def tag_line_for(self, node: Node):
        return get_text_in_language(self.g, self.lang, node, RDFS.comment, '')

    def description_for(self, node: Node, indent_prefix: str):
        return get_text_in_language(
            self.g, self.lang, node, DCTERMS.description, indent_prefix
        )

    def capability_number_for(self, capability_node, hint: str):
        for number in self.g.objects(capability_node, MATURITY_MODEL.capabilityNumber):
            log_item(f'{hint} Number', number)
            return str(number)
        raise value_error(f'{hint} has no capabilityNumber: {capability_node}')

    def local_name_for(self, subject_node: Node, hint: str) -> str:
        for local_name in self.g.objects(subject_node, MATURITY_MODEL.iriLocalName):
            log_item(f'{hint} Local Name', local_name)
            return str(local_name)
        raise value_error(f'{hint} has no iriLocalName: {subject_node}')

    def local_type_name_for(self, subject_node: Node, hint: str) -> str:
        type_node = self.get_type(subject_node)
        return self.local_type_name_for_type(type_node, hint)

    def local_type_name_for_type(self, type_node: Node, hint: str) -> str:
        for local_type_name in self.g.objects(
            type_node, MATURITY_MODEL.iriLocalTypeName
        ):
            # log_item(f"{hint} Local Type Name", local_type_name)
            return str(local_type_name)
        raise value_error(f'{hint} has no iriLocalTypeName: {type_node}')

    def get_type(self, subject_node):
        for node_type in self.g.objects(subject_node, RDF.type):
            if node_type in (OWL.Thing, OWL.NamedIndividual):
                continue
            return node_type

    def has_type(self, subject_uri, type_uri):
        return (subject_uri, RDF.type, type_uri) in self.g

    def has_type_pillar(self, subject_iri):
        return self.has_type(subject_iri, MATURITY_MODEL.Pillar)

    def has_type_level(self, subject_iri):
        return self.has_type(subject_iri, MATURITY_MODEL.Level)

    def has_type_capability_area(self, subject_iri):
        # if self.verbose:
        #     log_item("Type of", f"{subject_iri} == {self.get_type(subject_iri)}")
        return self.has_type(subject_iri, MATURITY_MODEL.CapabilityArea)

    def has_type_capability(self, subject_iri):
        # if self.verbose:
        #     log_item("Type of", f"{subject_iri} == {self.get_type(subject_iri)}")
        return self.has_type(subject_iri, MATURITY_MODEL.Capability)

    def subjects_of_type(self, type_uri: URIRef) -> Iterable[Node]:
        return self.g.subjects(predicate=RDF.type, object=type_uri)

    def model_nodes(self) -> Iterable[Node]:
        return self.subjects_of_type(type_uri=MATURITY_MODEL.Model)

    def models_non_cached(self):  # -> Generator[model.MaturityModel, Any, None]:
        from .model import MaturityModel

        for model_node in self.model_nodes():
            yield MaturityModel(graph=self, model_node=model_node, config=self.config)

    def models(self):
        if len(self._models) == 0:
            self._models = list(self.models_non_cached())
        return self._models

    def model_with_name(self, model_name: str):
        for model in self.models():
            if model.name == model_name:
                return model
        raise value_error(f'Model with name {model_name} does not exist')

    def capability_areas_of_pillar(self, pillar_node: Node) -> Iterable[Node]:
        found = 0
        for in_pillar_thing in self.g.subjects(
            predicate=MATURITY_MODEL.inPillar, object=pillar_node
        ):
            if self.has_type_capability_area(in_pillar_thing):
                found += 1
                yield in_pillar_thing
        if found == 0:
            warning(f'No capability areas found for pillar <{pillar_node}>')

    def capabilities_in_area(self, area_node: Node) -> Iterable[Node]:
        found = 0
        for in_area_thing in self.g.subjects(MATURITY_MODEL.inArea, area_node):
            if self.has_type_capability(in_area_thing):
                found += 1
                yield in_area_thing
        if found == 0:
            warning(f'No capabilities found in area <{area_node}>')

    def fragment_background_and_intro(self, subject_node):
        for fragment in self.g.objects(subject_node, MATURITY_MODEL.backgroundAndIntro):
            yield fragment

    def rewrite_fragment_references(self, fragments_root: Path):
        """
        For each reference to some text-fragment rewrite the path to that markdown file
        relative to the given input directory
        """
        log_item('Rewriting', 'Fragment References')
        predicate = MATURITY_MODEL.backgroundAndIntro
        for subject, objekt in self.g.subject_objects(predicate):
            log_item('Subject', subject)
            log_item('Object', objekt)
            log_item('Fragments Root', relpath(fragments_root, getcwd()))
            fragment_path = fragments_root / objekt
            log_item('Fragment Path', fragment_path)
            if not fragment_path.exists():
                raise value_error(f'Fragment {fragment_path} does not exist')
            self.g.remove((subject, predicate, objekt))
            self.g.add((subject, predicate, Literal(str(fragment_path))))

    def create_sort_keys(self):
        """Generate sortKeys for anything with an ekgmm:capabilityNumber"""
        for subject, capability_number in self.g.subject_objects(
            MATURITY_MODEL.capabilityNumber
        ):
            capability_number_parts = str(capability_number).split('.')
            if len(capability_number_parts) != 3:
                raise value_error(
                    f'{subject} has an invalid number: {capability_number}'
                )
            sort_key = f'{capability_number_parts[0]}.{capability_number_parts[1]:0>3}.{capability_number_parts[2]:0>3}'
            self.g.add((subject, MATURITY_MODEL.sortKey, Literal(sort_key)))

    def write_tag_line(self, md: MarkdownDocument, node: Node):
        tag_line = self.tag_line_for(node)
        if tag_line:
            md.new_line(f'_{tag_line}_', wrap_width=0)

    def write_description(self, md: MarkdownDocument, node: Node):
        dct_description = self.description_for(node, md.indent)
        if dct_description:
            md.new_line(dct_description, wrap_width=0)
