from pathlib import Path
from typing import Optional

from rdflib import OWL

from .File import makedirs
from .graph import MaturityModelGraph
from .model import MaturityModel
from .pillar import MaturityModelPillar
from ..namespace import MATURIY_MODEL
from .markdown_document import MarkdownDocument, MarkDownFile

OWL._fail = False  # workaround for this issue: https://github.com/RDFLib/OWL-RL/issues/53


class MaturityModelMarkdownGenerator:
    """Checks each `.ttl` file in the given repository directory
        TODO: Create abstract interface and use that to implement other formats to generate
        TODO: Support multiple `ekgmm:Model` instances, select the one you need via a parameter
    """
    graph: MaturityModelGraph
    model: MaturityModel
    mkdocs: bool
    output_root: Path
    md_file: Optional[MarkdownDocument] = None

    def __init__(self, graph: MaturityModelGraph, model_name: str, mkdocs: bool, output_root: Path):
        self.graph = graph
        self.mkdocs = mkdocs
        self.output_root = output_root

        self.model = MaturityModel(graph=self.graph, model_name=model_name, mkdocs=mkdocs, output_root=output_root)

        self.local_type_name = self.graph.local_type_name_for_type(
            MATURIY_MODEL.Pillar, MaturityModelPillar.class_label
        )
        self.full_dir = self.output_root / self.local_type_name
        makedirs(self.full_dir, "Model")
        self.full_path = self.full_dir / 'index.md'

    def generate(self):
        self.model.generate()

