import argparse
from pathlib import Path

from ekglib.maturity_model_parser.loader import MaturityModelLoader
from ekglib.maturity_model_parser.markdown_generator import MaturityModelMarkdownGenerator


def mkdocs_gen_files(model_root: Path, output_root: Path):
    loader = MaturityModelLoader(True, model_root)
    graph = loader.load()
    generator = MaturityModelMarkdownGenerator(graph, model_name="EKG/MM", mkdocs=True, output_root=output_root)
    generator.generate()
    # exporter = GraphExporter(graph)
    # return exporter.export(stream)
    return 0


def runit(args) -> int:
    loader = MaturityModelLoader(verbose=args.verbose, model_root=Path(args.input))
    graph = loader.load()
    generator = MaturityModelMarkdownGenerator(graph, model_name="EKG/MM", mkdocs=False, output_root=Path(args.output))
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
    parser.add_argument('--input', '-i', help='The input directory', required=True)
    parser.add_argument('--output', '-o', help='The output directory', required=True)
    parser.add_argument('--model', '-m', help='The name of the model', default="EKG/MM")

    return runit(parser.parse_args())


if __name__ == "__main__":
    exit(main())
