import argparse
from pathlib import Path

from ekglib.maturity_model_parser.loader import MaturityModelLoader
from ekglib.maturity_model_parser.markdown_generator import MaturityModelMarkdownGenerator


def mkdocs_gen_files(model_root: Path, output_root: Path, docs_root: Path, fragments_root: Path):
    loader = MaturityModelLoader(
        verbose=True,
        model_root=model_root,
        docs_root=docs_root,
        fragments_root=fragments_root
    )
    graph = loader.load()
    generator = MaturityModelMarkdownGenerator(graph, model_name="EKG/MM", mkdocs=True, output_root=output_root)
    generator.generate()
    # exporter = GraphExporter(graph)
    # return exporter.export(stream)
    return 0


def mkdocs_gen_files2(model_root: Path, output_root: Path, docs_root: Path, fragments_root: Path):
    loader = MaturityModelLoader(
        verbose=True,
        model_root=model_root,
        docs_root=docs_root,
        fragments_root=fragments_root
    )
    graph = loader.load()
    generator = MaturityModelMarkdownGenerator(graph, model_name="EKG/MM", mkdocs=False, output_root=output_root)
    generator.generate()
    # exporter = GraphExporter(graph)
    # return exporter.export(stream)
    return 0


def runit(args) -> int:
    loader = MaturityModelLoader(
        verbose=args.verbose,
        model_root=Path(args.model_root),
        docs_root=Path(args.docs_root),
        fragments_root=Path(args.fragments_root)
    )
    graph = loader.load()
    generator = MaturityModelMarkdownGenerator(graph, model_name=args.model, mkdocs=False,
                                               output_root=Path(args.output))
    generator.generate()
    # exporter = GraphExporter(graph)
    # return exporter.export(stream)
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.maturity_model_parser',
        description='Generates Markdown files for all capabilities found in the given directory',
        epilog='Currently only supports turtle.',
        allow_abbrev=False
    )
    parser.add_argument('--verbose', '-v', help='verbose output', default=False, action='store_true')
    parser.add_argument('--model-root', help='The input directory with the .ttl files', required=True)
    parser.add_argument('--docs-root', help='The input directory with the static .md files', required=True)
    parser.add_argument('--fragments-root',
                        help='The input directory with the static .md files that are included as '
                             'fragments or copied to the output directory', required=True
                        )
    parser.add_argument('--output', help='The output directory', required=True)
    parser.add_argument('--model', help='The name of the model', default="EKG/MM")

    return runit(parser.parse_args())


if __name__ == "__main__":
    exit(main())
