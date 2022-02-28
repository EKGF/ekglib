from typing import Optional, Iterable

import rdflib
from rdflib import Graph, RDF, OWL, URIRef
from rdflib.term import Node

from ekglib import log_item
from ekglib.log.various import value_error, warning
from ekglib.namespace import MATURIY_MODEL


class MaturityModelGraph:
    g: rdflib.Graph

    def __init__(self, g: Graph, verbose: bool, lang: str):
        self.g = g
        self.verbose = verbose
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

    def has_type_pillar(self, subject_iri):
        return self.has_type(subject_iri, MATURIY_MODEL.Pillar)

    def has_type_level(self, subject_iri):
        return self.has_type(subject_iri, MATURIY_MODEL.Level)

    def has_type_capability_area(self, subject_iri):
        if self.verbose:
            log_item("Type of", f"{subject_iri} == {self.get_type(subject_iri)}")
        return self.has_type(subject_iri, MATURIY_MODEL.CapabilityArea)

    def has_type_capability(self, subject_iri):
        if self.verbose:
            log_item("Type of", f"{subject_iri} == {self.get_type(subject_iri)}")
        return self.has_type(subject_iri, MATURIY_MODEL.Capability)

    def subjects_of_type(self, type_uri: URIRef) -> Iterable[Node]:
        return self.g.subjects(RDF.type, type_uri)

    def models(self):
        return self.g.subjects(RDF.type, MATURIY_MODEL.Model)

    def model_with_name(self, model_name: str):
        for model in self.models():
            name = self.name_for(model, "Model")
            if name == model_name:
                return model
        raise value_error(f"Model with name {model_name} does not exist")

    def pillars(self, model_node: Node):
        found = 0
        for pillar in self.g.subjects(MATURIY_MODEL.pillarInModel, model_node):
            found += 1
            yield pillar
        if found == 0:
            raise value_error(f"Model has no pillars: <{model_node}>")

    def get_pillar_with_name(self, model_node: Node, name: str) -> Node:
        for pillar in self.pillars(model_node):
            pillar_name = self.name_for(pillar, "Pillar")
            if pillar_name == name:
                return pillar

    def capability_areas_of_pillar(self, pillar_node: Node) -> Iterable[Node]:
        found = 0
        for in_pillar_thing in self.g.subjects(MATURIY_MODEL.inPillar, pillar_node):
            if self.has_type_capability_area(in_pillar_thing):
                found += 1
                yield in_pillar_thing
        if found == 0:
            warning(f"No capability areas found for pillar <{pillar_node}>")

    def capabilities_in_area(self, area_node: Node) -> Iterable[Node]:
        found = 0
        for in_area_thing in self.g.subjects(MATURIY_MODEL.inArea, area_node):
            if self.has_type_capability(in_area_thing):
                found += 1
                yield in_area_thing
        if found == 0:
            warning(f"No capabilities found in area <{area_node}>")





