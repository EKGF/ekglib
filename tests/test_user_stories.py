import os
import sys
import textwrap

from ekglib.user_story_parser.parse import main


class TestUserStoryParser:

    def test_user_story_parser(self, test_data_dir):
        test_output = f'{test_data_dir}/test-user-story-001.ttl.txt'

        sys.argv = [
            'pytest',
            '--input', f'{test_data_dir}/test-user-story-001.ttl',
            '--output', test_output,
            '--kgiri-base', 'https://kg.your-company.kom',
            '--kgiri-base-replace', 'https://placeholder.kg',
            '--verbose'
        ]
        main()
        with open(test_output) as f:
            actual = textwrap.dedent(f.read())
        os.remove(test_output)
        expected = textwrap.dedent('''\
            @prefix concept: <https://ekgf.org/ontology/concept/> .
            @prefix ekgp-uss: <https://ekgf.org/ontology/ekg-platform-story-service/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix story: <https://ekgf.org/ontology/user-story/> .
            @prefix use-case: <https://ekgf.org/ontology/use-case/> .
            @prefix xs: <http://www.w3.org/2001/XMLSchema#> .

            <https://kg.your-company.kom/id/user-story-00001-thing-new> a ekgp-uss:SPARQLStatement,
                    story:UserStory ;
                rdfs:label "Create a new Thing" ;
                ekgp-uss:hasNamedSparqlStatement "SELECT * WHERE { GRAPH ?g { ?s ?p ?o }}" ;
                ekgp-uss:shouldBeSuppliedBy <https://kg.your-company.kom/id/ekg-platform-story-service> ;
                use-case:usedIn <https://kg.your-company.kom/id/use-case-new-things> ;
                story:baseName "test_data" ;
                story:hasInput [ concept:hasConcept <https://kg.your-company.kom/id/concept-prov-activity> ;
                        story:randomIRI true ],
                    [ concept:hasConcept <https://kg.your-company.kom/id/concept-thing-iri> ;
                        story:randomIRI true ],
                    [ a story:MandatoryParameter ;
                        concept:hasConcept <https://kg.your-company.kom/id/concept-session-id> ] ;
                story:hasOutput [ concept:hasConcept <https://kg.your-company.kom/id/concept-thing-iri> ],
                    [ concept:hasConcept <https://kg.your-company.kom/id/concept-session-id> ],
                    [ concept:hasConcept <https://kg.your-company.kom/id/concept-prov-activity> ] ;
                story:hasPersona <https://kg.your-company.kom/id/persona-professional> ;
                story:key "new-thing" .
        
            <https://kg.your-company.kom/id/ekg-platform-story-service> a ekgp-uss:UserStoryService .
            
            <https://kg.your-company.kom/id/use-case-new-things> a use-case:UseCase .
            
            <https://kg.your-company.kom/id/concept-prov-activity> a concept:ClassConcept .
            
            <https://kg.your-company.kom/id/concept-session-id> a concept:PropertyConcept .
            
            <https://kg.your-company.kom/id/concept-thing-iri> a concept:ClassConcept .
        
        ''')  # noqa: W293
        #
        # TODO: In the expected output above we need to add the kgiri prefix
        #
        print(actual)
        assert expected == actual
