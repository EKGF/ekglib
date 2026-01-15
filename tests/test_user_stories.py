import os
import sys
import textwrap

from ekg_lib.user_story_parser.parse import main
from ekg_lib.exceptions import PrefixException


class TestUserStoryParser:
    def test_user_story_parser(self, kgiri_base, test_data_dir):
        test_output = f'{test_data_dir}/test-user-story-001.ttl.txt'

        sys.argv = [
            'pytest',
            '--input',
            f'{test_data_dir}/test-user-story-001.ttl',
            '--output',
            test_output,
            '--kgiri-base',
            kgiri_base,
            '--kgiri-base-replace',
            'https://placeholder.kg',
            '--verbose',
        ]
        main()
        with open(test_output) as f:
            actual = textwrap.dedent(f.read())
        os.remove(test_output)
        expected = textwrap.dedent(f'''\
            @prefix concept: <https://ekgf.org/ontology/concept/> .
            @prefix ekgp-uss: <https://ekgf.org/ontology/ekg-platform-story-service/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix story: <https://ekgf.org/ontology/user-story/> .
            @prefix use-case: <https://ekgf.org/ontology/use-case/> .
            @prefix xs: <http://www.w3.org/2001/XMLSchema#> .

            <{kgiri_base}/id/user-story-00001-thing-new> a ekgp-uss:SPARQLStatement,
                    story:UserStory ;
                rdfs:label "Create a new Thing" ;
                ekgp-uss:hasNamedSparqlStatement """PREFIX kggraph: <{kgiri_base}/graph/>
            SELECT * WHERE {{ GRAPH kggraph:foo {{ ?s ?p ?o }}}}""" ;
                ekgp-uss:shouldBeSuppliedBy <{kgiri_base}/id/ekg-platform-story-service> ;
                use-case:usedIn <{kgiri_base}/id/use-case-new-things> ;
                story:baseName "test_data" ;
                story:hasInput [ concept:hasConcept <{kgiri_base}/id/concept-prov-activity> ;
                        story:randomIRI true ],
                    [ concept:hasConcept <{kgiri_base}/id/concept-thing-iri> ;
                        story:randomIRI true ],
                    [ a story:MandatoryParameter ;
                        concept:hasConcept <{kgiri_base}/id/concept-session-id> ] ;
                story:hasOutput [ concept:hasConcept <{kgiri_base}/id/concept-thing-iri> ],
                    [ concept:hasConcept <{kgiri_base}/id/concept-session-id> ],
                    [ concept:hasConcept <{kgiri_base}/id/concept-prov-activity> ] ;
                story:hasPersona <{kgiri_base}/id/persona-professional> ;
                story:key "new-thing" .
        
            <{kgiri_base}/id/ekg-platform-story-service> a ekgp-uss:UserStoryService .
            
            <{kgiri_base}/id/use-case-new-things> a use-case:UseCase .
            
            <{kgiri_base}/id/concept-prov-activity> a concept:ClassConcept .
            
            <{kgiri_base}/id/concept-session-id> a concept:PropertyConcept .
            
            <{kgiri_base}/id/concept-thing-iri> a concept:ClassConcept .
        
        ''')  # noqa: W293
        print(actual)
        assert expected == actual

    def test_user_story_parser_with_different_iris(self, test_data_dir):
        test_output = f'{test_data_dir}/test-user-story-002.ttl.txt'
        # setting manually as these ovverride the defaults
        kgiri_base = 'https://uat.ekg.acme.net'
        kgiri_base_replace = 'https://ekg.acme.com'
        sys.argv = [
            'pytest',
            '--input',
            f'{test_data_dir}/test-user-story-002.ttl',
            '--output',
            test_output,
            '--kgiri-base',
            kgiri_base,
            '--kgiri-base-replace',
            kgiri_base_replace,
            '--verbose',
        ]
        main()
        with open(test_output) as f:
            actual = textwrap.dedent(f.read())
        os.remove(test_output)
        expected = textwrap.dedent(f'''\
            @prefix concept: <https://ekgf.org/ontology/concept/> .
            @prefix ekgp-uss: <https://ekgf.org/ontology/ekg-platform-story-service/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix story: <https://ekgf.org/ontology/user-story/> .
            @prefix use-case: <https://ekgf.org/ontology/use-case/> .
            @prefix xs: <http://www.w3.org/2001/XMLSchema#> .

            <{kgiri_base}/id/user-story-00001-thing-new> a ekgp-uss:SPARQLStatement,
                    story:UserStory ;
                rdfs:label "Create a new Thing" ;
                ekgp-uss:hasNamedSparqlStatement """PREFIX kggraph: <{kgiri_base}/graph/>
            SELECT * WHERE {{ GRAPH kggraph:foo {{ ?s ?p ?o }}}}""" ;
                ekgp-uss:shouldBeSuppliedBy <{kgiri_base}/id/ekg-platform-story-service> ;
                use-case:usedIn <{kgiri_base}/id/use-case-new-things> ;
                story:baseName "test_data" ;
                story:hasInput [ concept:hasConcept <{kgiri_base}/id/concept-prov-activity> ;
                        story:randomIRI true ],
                    [ concept:hasConcept <{kgiri_base}/id/concept-thing-iri> ;
                        story:randomIRI true ],
                    [ a story:MandatoryParameter ;
                        concept:hasConcept <{kgiri_base}/id/concept-session-id> ] ;
                story:hasOutput [ concept:hasConcept <{kgiri_base}/id/concept-thing-iri> ],
                    [ concept:hasConcept <{kgiri_base}/id/concept-session-id> ],
                    [ concept:hasConcept <{kgiri_base}/id/concept-prov-activity> ] ;
                story:hasPersona <{kgiri_base}/id/persona-professional> ;
                story:key "new-thing" .
        
            <{kgiri_base}/id/ekg-platform-story-service> a ekgp-uss:UserStoryService .
            
            <{kgiri_base}/id/use-case-new-things> a use-case:UseCase .
            
            <{kgiri_base}/id/concept-prov-activity> a concept:ClassConcept .
            
            <{kgiri_base}/id/concept-session-id> a concept:PropertyConcept .
            
            <{kgiri_base}/id/concept-thing-iri> a concept:ClassConcept .
        
        ''')  # noqa: W293
        print(actual)
        assert expected == actual

    def test_user_story_parser_with_missing_iris_from_env_fail(self, test_data_dir):
        test_output = f'{test_data_dir}/test-user-story-001.ttl.txt'
        # setting manually as these ovverride the defaults
        sys
        sys.argv = [
            'pytest',
            '--input',
            f'{test_data_dir}/test-user-story-001.ttl',
            '--output',
            test_output,
            '--verbose',
        ]
        try:
            main()
            assert False
        except PrefixException:
            assert True

    def test_user_story_parser_with_base_iris_from_env(self, test_data_dir):
        test_output = f'{test_data_dir}/test-user-story-001.ttl.txt'
        # setting manually as these ovverride the defaults
        os.environ['EKG_KGIRI_BASE'] = 'https://localhost:8080'
        os.environ['EKG_KGIRI_BASE_REPLACE'] = 'https://placeholder.kg'
        sys.argv = [
            'pytest',
            '--input',
            f'{test_data_dir}/test-user-story-001.ttl',
            '--output',
            test_output,
            '--verbose',
        ]
        main()
        del os.environ['EKG_KGIRI_BASE']
        del os.environ['EKG_KGIRI_BASE_REPLACE']
        with open(test_output) as f:
            actual = textwrap.dedent(f.read())
        os.remove(test_output)
        print(actual)
        assert len(actual) > 0
