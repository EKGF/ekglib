import argparse
import textwrap

from rdflib import Graph, URIRef, RDF

from ..data_source import set_cli_params as data_source_set_cli_params
from ..git import set_cli_params as git_set_cli_params
from ..kgiri import EKG_NS, set_kgiri_base, set_cli_params as kgiri_set_cli_params
from ..log import log, log_item, warning, log_iri, log_rule
from ..namespace import DATASET, TRANSFORM, DATAOPS
from ..sparql import SPARQLEndpoint, set_cli_params as sparql_set_cli_params


#
# TODO: Make rules link to other rules so that we can calculate the right
#       execution order.
# TODO: Specify per rule whether its generic or dataset-specific.
#
class TransformRulesExecute:
    """Finds each `rule.ttl` file in each subdirectory of `/metadata/transform` and executes the rule it describes
    against the given SPARQL s3_endpoint.
    """

    def __init__(self, args, sparql_endpoint: SPARQLEndpoint = None):

        self.args = args
        self.verbose = args.verbose
        self.data_source_code = args.data_source_code
        self.sparql_endpoint = sparql_endpoint
        self.g = self._query_all_rules()
        log_item('Found # rules', len(self.g))
        self._filter_out_unused()
        log_rule('Executing Transform Rules')
        log_item('Number of triples', len(self.g))
        self.list_rules()

    def _filter_out_unused(self):  # TODO: Finish this
        for rule in self.g.subjects(RDF.type, TRANSFORM.Rule):
            log_item('Rule', rule)

    def list_rules(self):
        log('Rules in execution order:')
        for index, key in enumerate(sorted(self.g.objects(None, TRANSFORM.term('sortKey')))):
            log_item(f'Rule {index + 1}', key)

    def _query_all_rules(self) -> Graph:
        log_item("Get Transform Rules", self.data_source_code)
        return self.sparql_endpoint.construct_and_convert(
            f"""\
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX kggraph: <{EKG_NS['KGGRAPH']}>
            PREFIX transform: <https://ekgf.org/ontology/step-transform/>

            CONSTRUCT {{
                ?rule ?p ?s .
                ?rule transform:fromGraph ?g .
            }}
            WHERE {{
                GRAPH kggraph:{self.data_source_code} {{
                    ?rule a transform:Rule .
                    ?rule ?p ?s .
                    BIND(localname(?rule) AS ?key)
                }}
            }}
            ORDER BY ?key
            """  # noqa: F541
        )

    def execute(self) -> int:
        #
        # We're looking up each rule IRI via the sort key to:
        # - ensure we're doing in the right sorted order
        # - ensure that regardless of the actual IRI (which may be obfuscated even) we'll find
        #   the rule anyway.
        #
        rule_iris = list(self.g.objects(None, TRANSFORM.sortKey))
        max_rules = len(rule_iris)
        for index, key in enumerate(sorted(rule_iris)):
            for rule_iri in self.g.subjects(TRANSFORM.sortKey, key):
                self.execute_rule(rule_iri, index, max_rules, key)
        return 0

    def execute_rule(self, rule_iri, index, max_, key):
        log_rule(f"Executing rule {index + 1}/{max_}: {key}")
        log_iri("Executing Rule", rule_iri)
        count = 0
        for sparql_rule in self.g.objects(rule_iri, TRANSFORM.hasSPARQLRule):
            count += 1
            self.sparql_endpoint.execute_sparql_statement(
                self.add_detail_to_sparql_statement(self.data_source_code, rule_iri, sparql_rule)
            )
        if count > 0:
            log_item("# SPARQL Rules", count)
        else:
            warning(f"Transform rule has no SPARQL rule: {rule_iri}")

    def add_detail_to_sparql_statement(self, dataset_code: str, rule_iri: URIRef, sparql_rule: str):
        #
        # We cannot use prefixes here because they might clash with the prefixes in sparql_rule
        #
        # TODO: Register provenance
        #
        graph_iri = f"{EKG_NS['KGGRAPH']}{dataset_code}"
        dataset_iri = f"{EKG_NS['KGIRI']}dataset-{dataset_code}"
        dataset_class_iri = f"{DATASET}Dataset"
        dataset_code_p_iri = f"{DATASET}datasetCode"
        dataset_in_graph_p_iri = f"{DATASET}inGraph"
        data_source_code_p_iri = f"{DATASET}dataSourceCode"
        executed_rule_p_iri = f"{TRANSFORM}executedRule"
        created_by_pipeline_p_iri = f"{DATAOPS}createdByPipeline"
        #
        # need to use self.data_source_code here, don't "fix" because
        # self.data_source_code is the code for the whole pipeline,
        # such as "metadata" whereas data_source_code can be "gleif" or "edmcouncil" etc
        #
        # TODO: Change data_source_code to data source
        #
        pipeline_iri = f"{EKG_NS['KGIRI']}dataops-pipeline-{self.data_source_code}"
        pipeline_class_iri = f"{DATAOPS}Pipeline"
        pipeline_produced_dataset_p_iri = f"{DATAOPS}hasProducedDataset"
        detail = f"""\
            INSERT DATA {{
                GRAPH <{graph_iri}> {{
                    <{dataset_iri}> a <{dataset_class_iri}> ;
                        <{dataset_code_p_iri}> "{dataset_code}" ;
                        <{executed_rule_p_iri}> <{rule_iri}> ;
                        <{dataset_in_graph_p_iri}> <{graph_iri}> ;
                        <{created_by_pipeline_p_iri}> <{pipeline_iri}> .
                    <{pipeline_iri}> a <{pipeline_class_iri}> ;
                        rdfs:label "Pipeline for Data Source \\"{self.data_source_code}\\"" ;
                        <{data_source_code_p_iri}> "{self.data_source_code}" ;
                        <{pipeline_produced_dataset_p_iri}> <{dataset_iri}> .
                }}
            }}
            ;
            """
        #
        # We have to execute the INSERT DATA rule first because some rules (the obfuscation rules)
        # even update the content that this INSERT DATA statement inserted.
        #
        return textwrap.dedent(detail) + sparql_rule


def main():
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.transform_rules_execute',
        description='Processes each rule.ttl file in the given directory and executes it against the given SPARQL '
                    's3_endpoint',
        epilog='Currently only supports turtle.',
        allow_abbrev=False
    )

    parser.add_argument('--verbose', '-v', help='verbose output', default=False, action='store_true')
    parser.add_argument('--static-datasets-root', help='The static datasets root, relevant when dataset-code=metadata')
    git_set_cli_params(parser)
    kgiri_set_cli_params(parser)
    data_source_set_cli_params(parser)
    sparql_set_cli_params(parser)

    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)

    processor = TransformRulesExecute(args, sparql_endpoint=SPARQLEndpoint(args))
    return processor.execute()


if __name__ == "__main__":
    exit(main())
