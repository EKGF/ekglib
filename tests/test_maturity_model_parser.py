import sys
from pathlib import Path

from rdflib import URIRef, Graph, RDFS
from rdflib.term import Literal

import ekglib
from ekglib import log_item
from ekglib.maturity_model_parser import MaturityModelLoader, Config, BASE_IRI_MATURITY_MODEL
from ekglib.maturity_model_parser.File import makedirs
from ekglib.maturity_model_parser.graph import get_text_in_language
from ekglib.maturity_model_parser.pages_yaml import PagesYaml

from ekglib.namespace import MATURIY_MODEL


class TestMaturityModelParser:

    def test_get_text_in_language1(self):
        graph = Graph()
        subject = URIRef("https://test")
        graph.add((subject, RDFS.comment, Literal("english", lang="en")))
        graph.add((subject, RDFS.comment, Literal("french", lang="fr")))
        graph.add((subject, RDFS.comment, Literal("nolang")))
        english = get_text_in_language(graph, 'en', subject, RDFS.comment)
        assert english == "english"
        french = get_text_in_language(graph, 'fr', subject, RDFS.comment)
        assert french == "french"
        dutch = get_text_in_language(graph, 'nl', subject, RDFS.comment)
        assert dutch == "nolang"

    def test_get_text_in_language2(self):
        graph = Graph()
        subject = URIRef("https://test")
        graph.add((subject, RDFS.comment, Literal("english", lang="en")))
        graph.add((subject, RDFS.comment, Literal("french", lang="fr")))
        english = get_text_in_language(graph, 'en', subject, RDFS.comment)
        assert english == "english"
        french = get_text_in_language(graph, 'fr', subject, RDFS.comment)
        assert french == "french"
        dutch = get_text_in_language(graph, 'nl', subject, RDFS.comment)
        assert dutch == "english"

    def test_pages_yaml(self, test_output_dir):
        yaml = PagesYaml(root=Path(test_output_dir), title="TestABC")
        yaml.add('somepage.md')
        yaml.add('otherpage.md')
        yaml.write()
        with open(f"{test_output_dir}/.pages.yaml") as f:
            lines = f.readlines()
        assert lines == [
            'title: TestABC\n',
            'nav:\n',
            '  - index.md\n',
            '  - somepage.md\n',
            '  - otherpage.md'
        ]

    def test_maturity_model_parser_001(self, test_data_dir, test_output_dir):
        docs_root = Path(f"{test_data_dir}/maturity-model/docs")
        fragments_root = Path(f"{test_data_dir}/maturity-model/docs-fragments")
        config = Config(
            model_name="Test EKG/MM",
            verbose=False,
            mkdocs=False,
            model_root=Path(f"{test_data_dir}/maturity-model"),
            docs_root=docs_root,
            fragments_root=fragments_root,
            output_root=Path(f"{test_output_dir}/ekgmm_test_001")
        )
        loader = MaturityModelLoader(config=config)
        graph = loader.load()
        log_item("models", graph)
        models = list(graph.models())
        assert len(models) == 1
        model = models[0]
        pillars = list(graph.pillars(model))
        assert len(pillars) == 4
        business_pillar = graph.get_pillar_with_name(model, "Business Pillar")
        assert business_pillar == MATURIY_MODEL.BusinessPillar
        areas = list(graph.capability_areas_of_pillar(business_pillar))
        assert len(areas) == 1
        area_strategy_actuation = areas[0]
        capabilities = list(graph.capabilities_in_area(area_strategy_actuation))
        assert len(capabilities) == 3

    def test_maturity_model_parser_002(self, test_output_dir, test_ekgmm_repo_dir):
        output_root = Path(f"{test_output_dir}/ekgmm_test_002")
        docs_root = output_root / 'docs'
        makedirs(docs_root, "abc")
        config = Config(
            model_name="EKG/MM",
            verbose=False,
            mkdocs=False,
            model_root=Path(test_ekgmm_repo_dir),
            docs_root=docs_root,
            fragments_root=Path(test_ekgmm_repo_dir) / 'docs-fragments',
            output_root=output_root
        )
        loader = MaturityModelLoader(config=config)
        graph = loader.load()
        models = list(graph.models())
        assert len(models) == 1
        model = graph.model_with_name("EKG/MM")
        pillars = list(graph.pillars(model))
        assert len(pillars) == 4
        business_pillar = graph.get_pillar_with_name(model, "Business Pillar")
        assert business_pillar == URIRef(f"{BASE_IRI_MATURITY_MODEL}business-pillar")
        areas = list(graph.capability_areas_of_pillar(business_pillar))
        assert len(areas) == 3
        area_strategy_actuation = areas[0]
        capabilities = list(graph.capabilities_in_area(area_strategy_actuation))
        assert len(capabilities) == 3

    def test_maturity_model_parser_003(self, test_data_dir, test_output_dir):
        sys.argv = [
            'pytest',
            '--model-root', f"{test_data_dir}/maturity-model",
            '--docs-root', f"{test_data_dir}/maturity-model/docs",
            '--fragments-root', f"{test_data_dir}/maturity-model",
            '--output', f"{test_output_dir}/ekgmm_test_003",
            '--model', "Test EKG/MM",
            '--verbose'
        ]
        assert 0 == ekglib.maturity_model_parser.main()

    def test_maturity_model_parser_004(self, test_ekgmm_repo_dir, test_ekgmm_docs_root, test_output_dir):
        log_item("Git repo dir", test_ekgmm_repo_dir)
        sys.argv = [
            'pytest',
            '--model-root', test_ekgmm_repo_dir,
            '--docs-root', test_ekgmm_docs_root,
            '--fragments-root', str((Path(test_ekgmm_docs_root) / "../docs-fragments").resolve()),
            '--output', f"{test_output_dir}/ekgmm_test_004",
            '--verbose'
        ]
        assert 0 == ekglib.maturity_model_parser.main()
