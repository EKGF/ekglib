import argparse
import textwrap

from rdflib import Graph, ConjunctiveGraph, URIRef, RDF
from SPARQLWrapper.Wrapper import QueryResult

from ..data_source import set_cli_params as data_source_set_cli_params
from ..git import set_cli_params as git_set_cli_params
from ..kgiri import EKG_NS, set_kgiri_base, set_cli_params as kgiri_set_cli_params
from ..log import log, log_item, warning, log_iri, log_rule
from ..namespace import DATASET, RULE, DATAOPS
from ..sparql import SPARQLEndpoint, set_cli_params as sparql_set_cli_params


#
# TODO: Make rules link to other rules so that we can calculate the right
#       execution order.
# TODO: Specify per rule whether its generic or dataset-specific.
#
class DataopsRulesExecute:
    """Finds each `rule.ttl` file in each subdirectory of `/metadata` and executes the rule it describes
    against the given SPARQL s3_endpoint.
    """

    def __init__(self, args, sparql_endpoint: SPARQLEndpoint = None):

        self.args = args
        self.verbose = args.verbose
        self.data_source_code = args.data_source_code
        self.rules_file = args.rules_file
        self.rule_type = URIRef(args.rule_type)
        self.sparql_endpoint = sparql_endpoint
        if self.rules_file is None:
            self.g = self._query_all_rules().convert()
        else:
            self.g = Graph().parse(self.rules_file, format='ttl')
        log_item('Found # rules', len(list(self.g.subjects( RDF.type, RULE.term(self.rule_type)))))
        self._filter_out_unused()
        log_rule('Executing Dataops Rules')
        log_item('Number of triples', len(self.g))
        self.list_rules()

    def _filter_out_unused(self):  # TODO: Finish this
        for rule in self.g.subjects(RDF.type, RULE.Rule):
            log_item('Rule', rule)

    def list_rules(self):
        log('Rules in execution order:')
        for index, key in enumerate(sorted(self.g.objects(None, RULE.term('sortKey')))):
            log_item(f'Rule {index + 1}', key)

    def _query_all_rules(self) -> Graph:
        log_item("Get Dataops Rules", self.data_source_code)
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
        for index, key in enumerate(sorted(rule_iris)):
            for rule_iri in self.g.subjects(RULE.sortKey, key):
                rc+=self.execute_rule(rule_iri, index, max_rules, key)
        return rc

    def execute_rule(self, rule_iri, index, max_, key):
        log_rule(f"Executing rule {index + 1}/{max_}: {key}")
        log_iri("Executing Rule", rule_iri)
        count = 0
        if self.rule_type == RULE.ObfuscationRule:
            # add details of the obfucation rule being executed to the dataset first so it can also be obfuscated
            self.sparql_endpoint.execute_sparql_statement(self.insert_detail_about_sparql_statement(self.data_source_code, rule_iri ))
        for sparql_rule in self.g.objects(rule_iri, RULE.hasSPARQLRule):
            count += 1
            validation_result = None
            for statement_type in self.g.objects(rule_iri, RULE.sparqlQueryType):

                if statement_type == RULE.SPARQLSelectQuery:
                    result=self.sparql_endpoint.execute_sparql_select_query(sparql_rule)
                    if result is not None:
                        formatted_response = format(result.response.read().decode('utf-8'))
                elif statement_type == RULE.SPARQLConstructQuery:
                    result=self.sparql_endpoint.execute_construct(sparql_rule)
                    if result is not None:
                        graph = result.convert()
                elif statement_type == RULE.SPARQLAskQuery:
                    result=self.sparql_endpoint.execute_sparql_statement(sparql_rule)
                    if result is not None:
                        actual_result = format(result.response.read().decode('utf-8'))
                        for expected_result in self.g.objects(rule_iri, RULE.expectedResult):
                            if expected_result == RULE.BooleanResultTrue and actual_result == 'true':
                                validation_result=RULE.ValidationRulePass
                            elif expected_result == RULE.BooleanResultFalse and actual_result == 'false':
                                validation_result=RULE.ValidationRulePass
                            else:
                                validation_result=RULE.ValidationRuleFail
                elif statement_type == RULE.SPARQLUpdateStatement:
                    result=self.sparql_endpoint.execute_sparql_statement(sparql_rule)
                    if result is not None:
                        formatted_response = format(result.response.read().decode('utf-8'))
                else:
                    continue
                #  details of obfucation rules have already been added so should not be included here
                if self.rule_type != RULE.ObfuscationRule:
                    if validation_result is None:
                        self.sparql_endpoint.execute_sparql_statement(self.insert_detail_about_sparql_statement(self.data_source_code, rule_iri ))
                    else:
                        self.sparql_endpoint.execute_sparql_statement(self.insert_detail_about_sparql_statement(self.data_source_code, rule_iri, validation_result))
                        if validation_result == RULE.ValidationRuleFail:
                            for severity in self.g.objects(rule_iri, RULE.severity):
                                if severity == RULE.Violation:
                                    return 1
        if count > 0:
            log_item("# SPARQL Rules", count)
        else:
            warning(f"Story validation rule has no SPARQL rule: {rule_iri}")
        return 0

    def insert_detail_about_sparql_statement(self, dataset_code: str, rule_iri: URIRef, result=None):
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
        executed_rule_p_iri = f"{RULE}executedRule"
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
        tail_detail = f"""\
                }}
            }}
            
        """
        result_detail = f"""\
                    <{rule_iri}> <{RULE}validationResult> <{result}> .
        """

        if result is None:
            return textwrap.dedent(core_detail + tail_detail)
        else:
            return textwrap.dedent(core_detail + result_detail + tail_detail)


def main():
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.dataops_rules_execute',
        description='Processes each rule.ttl file in the given directory and executes it against the given SPARQL '
                    's3_endpoint',
        epilog='Currently only supports turtle.',
        allow_abbrev=False
    )

    parser.add_argument('--verbose', '-v', help='verbose output', default=False, action='store_true')
    parser.add_argument('--static-datasets-root', help='The static datasets root, relevant when dataset-code=metadata')
    parser.add_argument('--rules-file', help='Optional aternative source of rules', default=None )
    parser.add_argument('--rule-type', help='Type of rules to be executed', default=None )
    git_set_cli_params(parser)
    kgiri_set_cli_params(parser)
    data_source_set_cli_params(parser)
    sparql_set_cli_params(parser)

    args = parser.parse_args()
    set_kgiri_base(args.kgiri_base)

    processor = DataopsRulesExecute(args, sparql_endpoint=SPARQLEndpoint(args))
    return processor.execute()


if __name__ == "__main__":
    exit(main())
