# noqa
import argparse
import textwrap
from typing import Any

from rdflib import RDF, Graph, URIRef

from ..data_source import set_cli_params as data_source_set_cli_params
from ..git import set_cli_params as git_set_cli_params
from ..kgiri import EKG_NS, set_kgiri_base
from ..kgiri import set_cli_params as kgiri_set_cli_params
from ..log import log, log_iri, log_item, log_rule, warning
from ..namespace import DATAOPS, DATASET, RULE
from ..sparql import SPARQLEndpoint
from ..sparql import set_cli_params as sparql_set_cli_params
from ..sparql.sparql_endpoint import SPARQLResponse


#
# TODO: Make rules link to other rules so that we can calculate the right
#       execution order.
# TODO: Specify per rule whether its generic or dataset-specific.
#
class DataopsRulesExecute:
    """Finds each `rule.ttl` file in each subdirectory of `/metadata` and executes the rule it describes
    against the given SPARQL s3_endpoint.
    """

    def __init__(
        self, args: argparse.Namespace, sparql_endpoint: SPARQLEndpoint | None = None
    ) -> None:
        self.args = args
        self.verbose = args.verbose
        self.data_source_code = args.data_source_code
        self.rules_file = args.rules_file
        self.rule_type = URIRef(args.rule_type)
        self.sparql_endpoint = sparql_endpoint
        if self.rules_file is None:
            result = self._query_all_rules()
            if result is None:
                self.g = Graph()
            else:
                converted = result.convert()  # type: ignore[attr-defined]
                if not isinstance(converted, Graph):
                    raise ValueError(f'Expected Graph, got {type(converted)}')
                self.g = converted
        else:
            self.g = Graph().parse(self.rules_file, format='ttl')
        log_item('Found # rules', len(list(self.g.subjects(RDF.type, self.rule_type))))
        self._filter_out_unused()
        log_rule('Executing Dataops Rules')
        log_item('Number of triples', len(self.g))
        self.list_rules()

    def _filter_out_unused(self) -> None:  # TODO: Finish this
        for rule in self.g.subjects(RDF.type, RULE.Rule):
            log_item('Rule', rule)

    def list_rules(self) -> None:
        log('Rules in execution order:')
        for index, key in enumerate(
            sorted(self.g.objects(None, RULE.term('sortKey')), key=str)
        ):
            log_item(f'Rule {index + 1}', key)

    def _query_all_rules(self) -> SPARQLResponse | None:
        if self.sparql_endpoint is None:
            raise ValueError('sparql_endpoint is required')
        log_item('Get Dataops Rules', self.data_source_code)
        return self.sparql_endpoint.execute_construct(
            f"""\
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX kggraph: <{EKG_NS['KGGRAPH']}>
            PREFIX rule: <https://ekgf.org/ontology/dataops-rule/>

            CONSTRUCT {{
                ?rule ?p ?s .
                ?rule rule:fromGraph ?g .
            }}
            WHERE {{
                GRAPH kggraph:{self.data_source_code} {{
                    ?rule a <{self.rule_type}> .
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
        rule_iris = list(self.g.objects(None, RULE.sortKey))
        max_rules = len(rule_iris)
        rc = 0
        for index, key in enumerate(sorted(rule_iris, key=str)):
            for rule_iri in self.g.subjects(RULE.sortKey, key):
                if not isinstance(rule_iri, URIRef):
                    continue
                rc += self.execute_rule(rule_iri, index, max_rules, key)
        return rc

    def execute_rule(self, rule_iri: URIRef, index: int, max_: int, key: Any) -> int:  # noqa: C901
        if self.sparql_endpoint is None:
            raise ValueError('sparql_endpoint is required')
        log_rule(f'Executing rule {index + 1}/{max_}: {key}')
        log_iri('Executing Rule', rule_iri)
        count = 0
        if self.rule_type == RULE.ObfuscationRule:
            # add details of the obfucation rule being executed to the dataset first so it can also be obfuscated
            self.sparql_endpoint.execute_sparql_statement(
                self.insert_detail_about_sparql_statement(
                    self.data_source_code, rule_iri
                )
            )
        for sparql_rule in self.g.objects(rule_iri, RULE.hasSPARQLRule):
            count += 1
            validation_result = None
            sparql_rule_str = str(sparql_rule)
            for statement_type in self.g.objects(rule_iri, RULE.sparqlQueryType):
                if statement_type == RULE.SPARQLSelectQuery:
                    result = self.sparql_endpoint.execute_sparql_select_query(
                        sparql_rule_str
                    )
                    if result is not None:
                        # Read and decode response (result used for side effects)
                        result.response.read().decode('utf-8')
                elif statement_type == RULE.SPARQLConstructQuery:
                    construct_result: Any = self.sparql_endpoint.execute_construct(
                        sparql_rule_str
                    )
                    if construct_result is not None:
                        # Convert result (result used for side effects)
                        if hasattr(construct_result, 'convert'):
                            construct_result.convert()  # type: ignore[attr-defined]
                elif statement_type == RULE.SPARQLAskQuery:
                    result = self.sparql_endpoint.execute_sparql_statement(
                        sparql_rule_str
                    )
                    if result is not None:
                        actual_result = format(result.response.read().decode('utf-8'))
                        for expected_result in self.g.objects(
                            rule_iri, RULE.expectedResult
                        ):
                            if (
                                expected_result == RULE.BooleanResultTrue
                                and actual_result == 'true'
                            ):
                                validation_result = RULE.ValidationRulePass
                            elif (
                                expected_result == RULE.BooleanResultFalse
                                and actual_result == 'false'
                            ):
                                validation_result = RULE.ValidationRulePass
                            else:
                                validation_result = RULE.ValidationRuleFail
                elif statement_type == RULE.SPARQLUpdateStatement:
                    result = self.sparql_endpoint.execute_sparql_statement(
                        str(sparql_rule)
                    )
                    if result is not None:
                        # Read and decode response (result used for side effects)
                        result.response.read().decode('utf-8')
                else:
                    continue
                #  details of obfucation rules have already been added so should not be included here
                if self.rule_type != RULE.ObfuscationRule:
                    if validation_result is None:
                        self.sparql_endpoint.execute_sparql_statement(
                            self.insert_detail_about_sparql_statement(
                                self.data_source_code, rule_iri
                            )
                        )
                    else:
                        self.sparql_endpoint.execute_sparql_statement(
                            self.insert_detail_about_sparql_statement(
                                self.data_source_code, rule_iri, validation_result
                            )
                        )
                        if validation_result == RULE.ValidationRuleFail:
                            for severity in self.g.objects(rule_iri, RULE.severity):
                                if severity == RULE.Violation:
                                    return 1
        if count > 0:
            log_item('# SPARQL Rules', count)
        else:
            warning(f'Story validation rule has no SPARQL rule: {rule_iri}')
        return 0

    def insert_detail_about_sparql_statement(
        self, dataset_code: str, rule_iri: URIRef, result: Any | None = None
    ) -> str:
        #
        # We cannot use prefixes here because they might clash with the prefixes in sparql_rule
        #
        # TODO: Register provenance
        #
        graph_iri = f'{EKG_NS["KGGRAPH"]}{dataset_code}'
        dataset_iri = f'{EKG_NS["KGIRI"]}dataset-{dataset_code}'
        dataset_class_iri = f'{DATASET}Dataset'
        dataset_code_p_iri = f'{DATASET}datasetCode'
        dataset_in_graph_p_iri = f'{DATASET}inGraph'
        data_source_code_p_iri = f'{DATASET}dataSourceCode'
        executed_rule_p_iri = f'{RULE}executedRule'
        created_by_pipeline_p_iri = f'{DATAOPS}createdByPipeline'
        #
        # need to use self.data_source_code here, don't "fix" because
        # self.data_source_code is the code for the whole pipeline,
        # such as "metadata" whereas data_source_code can be "gleif" or "edmcouncil" etc
        #
        # TODO: Change data_source_code to data source
        #
        pipeline_iri = f'{EKG_NS["KGIRI"]}dataops-pipeline-{self.data_source_code}'
        pipeline_class_iri = f'{DATAOPS}Pipeline'
        pipeline_produced_dataset_p_iri = f'{DATAOPS}hasProducedDataset'
        core_detail = f"""\
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
            """
        tail_detail = """\
                }
            }
            
        """
        result_detail = f"""\
                    <{rule_iri}> <{RULE}validationResult> <{result}> .
        """

        if result is None:
            return textwrap.dedent(core_detail + tail_detail)
        else:
            return textwrap.dedent(core_detail + result_detail + tail_detail)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.dataops_rules_execute',
        description='Processes each rule.ttl file in the given directory and executes it against the given SPARQL '
        's3_endpoint',
        epilog='Currently only supports turtle.',
        allow_abbrev=False,
    )

    parser.add_argument(
        '--verbose', '-v', help='verbose output', default=False, action='store_true'
    )
    parser.add_argument(
        '--static-datasets-root',
        help='The static datasets root, relevant when dataset-code=metadata',
    )
    parser.add_argument(
        '--rules-file', help='Optional aternative source of rules', default=None
    )
    parser.add_argument(
        '--rule-type', help='Type of rules to be executed', default=None
    )
    git_set_cli_params(parser)
    kgiri_set_cli_params(parser)
    data_source_set_cli_params(parser)
    sparql_set_cli_params(parser)

    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)

    processor = DataopsRulesExecute(args, sparql_endpoint=SPARQLEndpoint(args))
    return processor.execute()


if __name__ == '__main__':
    exit(main())
    exit(main())
