import argparse
import option
from pathlib import Path

from ekglib.maturity_model_parser.config import Config
from ekglib.maturity_model_parser.loader import MaturityModelLoader
from ekglib.maturity_model_parser.markdown_generator import (
    MaturityModelMarkdownGenerator,
)


def run_with_config(config: Config) -> int:
    loader = MaturityModelLoader(config)
    graph = loader.load()
    generator = MaturityModelMarkdownGenerator(graph, config)
    generator.generate()
    # exporter = GraphExporter(graph)
    # return exporter.export(stream)
    return 0


def run_with_args(args) -> int:
    if args.pillar_dir_name is None:
        pillar_dir_name: option.Option[str] = option.NONE  # type: ignore[assignment]
    else:
        pillar_dir_name = option.Some(args.pillar_dir_name)

    config = Config(
        model_name=args.model,
        verbose=args.verbose,
        mkdocs=False,
        model_root=Path(args.model_root),
        docs_root=Path(args.docs_root),
        fragments_root=Path(args.fragments_root),
        output_root=Path(args.output),
        pillar_dir_name=pillar_dir_name,
    )
    return run_with_config(config)


def main():
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.maturity_model_parser',
        description='Generates Markdown files for all capabilities found in the given directory',
        epilog='Currently only supports turtle.',
        allow_abbrev=False,
    )
    parser.add_argument(
        '--verbose', '-v', help='verbose output', default=False, action='store_true'
    )
    parser.add_argument(
        '--model-root', help='The input directory with the .ttl files', required=True
    )
    parser.add_argument(
        '--docs-root',
        help='The input directory with the static .md files',
        required=True,
    )
    parser.add_argument(
        '--fragments-root',
        help='The input directory with the static .md files that are included as '
        'fragments or copied to the output directory',
        required=True,
    )
    parser.add_argument(
        '--pillar-dir-name',
        help='The name of the top level directory under "./docs" where we '
        'generate content',
        required=False,
    )
    parser.add_argument('--output', help='The output directory', required=True)
    parser.add_argument('--model', help='The name of the model', default='EKG/Maturity')

    return run_with_args(parser.parse_args())


if __name__ == '__main__':
    exit(main())
