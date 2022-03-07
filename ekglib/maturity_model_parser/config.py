from pathlib import Path

from ekglib.log.various import value_error


class Config:

    def __init__(
            self,
            model_name: str,
            verbose: bool,
            mkdocs: bool,
            model_root: Path,
            docs_root: Path,
            output_root: Path,
            fragments_root: Path
    ):
        self.model_name = model_name
        self.verbose = verbose
        self.mkdocs = mkdocs
        self.model_root = model_root
        self.docs_root = docs_root
        self.output_root = output_root
        self.fragments_root = fragments_root

        if not self.model_root.is_dir():
            raise value_error("{} is not a valid directory", self.model_root.name)
        if not self.docs_root.is_dir():
            raise value_error("{} is not a valid directory", self.docs_root.name)
        if not self.fragments_root.is_dir():
            raise value_error("{} is not a valid directory", self.fragments_root.name)
