import sys
from pathlib import Path

from rdflib import URIRef

import ekglib
from ekglib import log_item
from ekglib.maturity_model_parser import MaturityModelLoader


class TestMaturityModelParser:

    def test_maturity_model_parser_001(self, test_data_dir):
        loader = MaturityModelLoader(verbose=True, model_root=Path(f"{test_data_dir}/maturity-model"))
        graph = loader.load()
        models = list(graph.models())
        assert len(models) == 1
        model = models[0]
        pillars = list(graph.pillars(model))
        assert len(pillars) == 4
        business_pillar = graph.get_pillar_with_name(model, "Business Pillar")
        assert business_pillar == URIRef("https://ekgf.github.io/ekglib/ontology/maturity-model/BusinessPillar")
        areas = list(graph.capability_areas_of_pillar(business_pillar))
        assert len(areas) == 1
        area_strategy_actuation = areas[0]
        capabilities = list(graph.capabilities_in_area(area_strategy_actuation))
        assert len(capabilities) == 3

    def test_maturity_model_parser_002(self, test_ekgmm_repo_dir):
        loader = MaturityModelLoader(verbose=False, model_root=Path(test_ekgmm_repo_dir))
        graph = loader.load()
        models = list(graph.models())
        assert len(models) == 2
        model = graph.model_with_name("EKG/MM")
        pillars = list(graph.pillars(model))
        assert len(pillars) == 4
        business_pillar = graph.get_pillar_with_name(model, "Business Pillar")
        assert business_pillar == URIRef("https://maturity-model.ekgf.org/business-pillar")
        areas = list(graph.capability_areas_of_pillar(business_pillar))
        assert len(areas) == 3
        area_strategy_actuation = areas[0]
        capabilities = list(graph.capabilities_in_area(area_strategy_actuation))
        assert len(capabilities) == 3

    def test_maturity_model_parser_003(self, test_data_dir, test_output_dir):
        sys.argv = [
            'pytest',
            '--model-root', f"{test_data_dir}/maturity-model",
            '--docs-root', f"{test_output_dir}/ekgmm_test_003",
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

