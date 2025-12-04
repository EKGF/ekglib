import sys
from os import getcwd
from os.path import relpath

import option
from pathlib import Path
from rdflib import URIRef, Graph, RDFS
from rdflib.term import Literal

import ekglib
from ekglib import log_item, log
from ekglib.namespace import BASE_IRI_MATURITY_MODEL
from ekglib.maturity_model_parser import MaturityModelLoader, Config
from ekglib.maturity_model_parser.File import makedirs
from ekglib.maturity_model_parser.graph import get_text_in_language
from ekglib.maturity_model_parser.pages_yaml import PagesYaml


class TestMaturityModelParser:
    def test_get_text_in_language1(self):
        graph = Graph()
        subject = URIRef('https://test')
        graph.add((subject, RDFS.comment, Literal('english', lang='en')))
        graph.add((subject, RDFS.comment, Literal('french', lang='fr')))
        graph.add((subject, RDFS.comment, Literal('nolang')))
        english = get_text_in_language(graph, 'en', subject, RDFS.comment, '')
        assert english == 'english'
        french = get_text_in_language(graph, 'fr', subject, RDFS.comment, '')
        assert french == 'french'
        dutch = get_text_in_language(graph, 'nl', subject, RDFS.comment, '')
        assert dutch == 'nolang'

    def test_get_text_in_language2(self):
        graph = Graph()
        subject = URIRef('https://test')
        graph.add((subject, RDFS.comment, Literal('english', lang='en')))
        graph.add((subject, RDFS.comment, Literal('french', lang='fr')))
        english = get_text_in_language(graph, 'en', subject, RDFS.comment, '')
        assert english == 'english'
        french = get_text_in_language(graph, 'fr', subject, RDFS.comment, '')
        assert french == 'french'
        dutch = get_text_in_language(graph, 'nl', subject, RDFS.comment, '')
        assert dutch == 'english'

    def test_pages_yaml(self, test_output_dir):
        yaml = PagesYaml(root=Path(test_output_dir), title='TestABC')
        yaml.add('somepage.md')
        yaml.add('otherpage.md')
        yaml.write()
        with open(f'{test_output_dir}/.pages.yaml') as f:
            lines = f.readlines()
        assert lines == [
            'title: TestABC\n',
            'nav:\n',
            '  - index.md\n',
            '  - somepage.md\n',
            '  - otherpage.md',
        ]

    def test_maturity_model_parser_001(self, test_data_dir, test_output_dir):
        log('Starting test_maturity_model_parser_001:')
        docs_root = Path(f'{test_data_dir}/maturity-model/docs')
        fragments_root = Path(f'{test_data_dir}/maturity-model/docs-fragments')
        config = Config(
            model_name='EKG/Maturity',
            verbose=False,
            mkdocs=False,
            model_root=Path(f'{test_data_dir}/maturity-model'),
            docs_root=docs_root,
            fragments_root=fragments_root,
            output_root=Path(f'{test_output_dir}/ekgmm_test_001'),
            pillar_dir_name=option.NONE,
        )
        loader = MaturityModelLoader(config=config)
        graph = loader.load()
        log_item('models', graph)
        models = graph.models()
        assert len(models) == 1
        model = models[0]
        pillars = model.pillars()
        assert len(pillars) == 4
        business_pillars = list(model.get_pillars_with_name('Business Pillar'))
        assert len(business_pillars) == 1
        for business_pillar in business_pillars:
            assert business_pillar.node == URIRef(
                'business-pillar', BASE_IRI_MATURITY_MODEL
            )
            areas = business_pillar.capability_areas()
            assert len(areas) == 1
            area_strategy_actuation = areas[0]
            log_item('area', area_strategy_actuation.node)
            capabilities = list(area_strategy_actuation.capabilities())
            log_item('# capabilities', len(capabilities))
            assert len(capabilities) == 3

    def test_maturity_model_parser_002(self, test_output_dir, test_ekgmm_repo_dir):
        log('Starting test_maturity_model_parser_002:')
        output_root = Path(f'{test_output_dir}/ekgmm_test_002')
        docs_root = output_root / 'docs'
        makedirs(docs_root, 'Test 002 Output')
        config = Config(
            model_name='EKG/Maturity',
            verbose=True,
            mkdocs=False,
            model_root=Path(test_ekgmm_repo_dir),
            docs_root=docs_root,
            fragments_root=Path(test_ekgmm_repo_dir) / 'docs-fragments',
            output_root=output_root,
            pillar_dir_name=option.NONE,
        )
        loader = MaturityModelLoader(config=config)
        graph = loader.load()
        models = list(graph.model_nodes())
        log_item('# models', len(models))
        assert len(models) == 1
        model = graph.model_with_name('EKG/Maturity')
        pillars = model.pillars()
        log_item('# pillars', len(pillars))
        assert len(pillars) == 4
        business_pillars = list(model.get_pillars_with_name('Business Pillar'))
        assert len(business_pillars) == 1
        business_pillar = business_pillars[0]
        assert business_pillar.node == URIRef(
            f'{BASE_IRI_MATURITY_MODEL}business-pillar'
        )
        areas = business_pillar.capability_areas()
        assert len(areas) == 3
        area_strategy_actuation = areas[0]
        capabilities = area_strategy_actuation.capabilities()
        assert len(capabilities) == 3

    def test_maturity_model_parser_003(self, test_data_dir, test_output_dir):
        log('Starting test_maturity_model_parser_003:')
        sys.argv = [
            'pytest',
            '--model-root',
            f'{test_data_dir}/maturity-model',
            '--docs-root',
            f'{test_data_dir}/maturity-model/docs',
            '--fragments-root',
            f'{test_data_dir}/maturity-model',
            '--output',
            f'{test_output_dir}/ekgmm_test_003',
            '--model',
            'EKG/Maturity',
            '--verbose',
        ]
        assert 0 == ekglib.maturity_model_parser.main()

    def test_maturity_model_parser_004(
        self, test_ekgmm_repo_dir, test_ekgmm_docs_root, test_ekgmm_output_dir
    ):
        log('Starting test_maturity_model_parser_004:')
        model_root = str((Path(test_ekgmm_docs_root) / '../metadata').resolve())
        log_item('Model Root', relpath(model_root, getcwd()))
        fragments_root = str(
            (Path(test_ekgmm_docs_root) / '../docs-fragments').resolve()
        )
        log_item('Fragments Root', relpath(fragments_root, getcwd()))
        sys.argv = [
            'pytest',
            '--verbose',
            '--model-root',
            model_root,
            '--docs-root',
            test_ekgmm_docs_root,
            '--fragments-root',
            fragments_root,
            '--output',
            test_ekgmm_output_dir,
            '--pillar-dir-name',
            'pillar-dev',
        ]
        assert 0 == ekglib.maturity_model_parser.main()
