import argparse
import textwrap

from rdflib import Graph, URIRef, RDF

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
class StoryValidateRulesExecute:
    """Finds each `rule.ttl` file in each subdirectory of `/metadata/story-validate` and executes the rule it describes
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
        log_rule('Executing Story Validation Rules')
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
        log_item("Get Story Validation Rules", self.data_source_code)
        return self.sparql_endpoint.construct_and_convert(
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
                    ?rule a rule:ValidationRule .
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
        for index, key in enumerate(sorted(rule_iris)):
            for rule_iri in self.g.subjects(RULE.sortKey, key):
                self.execute_rule(rule_iri, index, max_rules, key)
        return 0

    def execute_rule(self, rule_iri, index, max_, key):
        log_rule(f"Executing rule {index + 1}/{max_}: {key}")
        log_iri("Executing Rule", rule_iri)
        count = 0
        for sparql_rule in self.g.objects(rule_iri, RULE.hasSPARQLRule):
            count += 1
            self.sparql_endpoint.execute_sparql_statement(sparql_rule)
        if count > 0:
            log_item("# SPARQL Rules", count)
        else:
            warning(f"Story validation rule has no SPARQL rule: {rule_iri}")


def main():
    parser = argparse.ArgumentParser(
        prog='python3 -m ekglib.story_validate_rules_execute',
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

    processor = StoryValidateRulesExecute(args, sparql_endpoint=SPARQLEndpoint(args))
    return processor.execute()


if __name__ == "__main__":
    exit(main())
