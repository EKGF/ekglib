from __future__ import annotations

from pathlib import Path
from typing import Any

import rdflib
from rdflib import OWL, Graph

from ..log.various import log_item, warning

OWL._fail = (
    False  # workaround for this issue: https://github.com/RDFLib/OWL-RL/issues/53
)


class GraphExporter:
    """Exports a given RDF Graph to the given output file or stream"""

    g: rdflib.Graph

    def __init__(self, g: Graph):
        self.g = g

    def export(self, output: str | Path | Any) -> int:
        if not output:
            warning(
                'You did not specify an output file or stream, no output file created'
            )
            return 1
        if isinstance(output, str):
            log_item('Writing output to', output)
        self.g.serialize(destination=output, format='ttl')
        if isinstance(output, str):
            log_item('Created', output)
        return 0
        return 0
