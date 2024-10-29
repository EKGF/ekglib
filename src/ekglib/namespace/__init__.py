from rdflib import Namespace

BASE_IRI_MATURITY_MODEL = 'https://maturity.ekgf.org/id/'

MATURITY_MODEL = Namespace(
    'https://raw.githubusercontent.com/EKGF/ontology-maturity-model/main/maturity-model.ttl#'
)
USERSTORY = Namespace('https://ekgf.org/ontology/user-story/')
RULE = Namespace('https://ekgf.org/ontology/dataops-rule/')
DATAOPS = Namespace('https://ekgf.org/ontology/dataops/')
DATASET = Namespace('https://ekgf.org/ontology/dataset/')
USECASE = Namespace('https://ekgf.org/ontology/use-case/')
PERSONA = Namespace('https://ekgf.org/ontology/persona/')
CONCEPT = Namespace('https://ekgf.org/ontology/concept/')
EKGPSS = Namespace('https://ekgf.org/ontology/ekg-platform-story-service/')
LDAP = Namespace('https://ekgf.org/ontology/ldap/')
PROV = Namespace('http://www.w3.org/ns/prov#')
RAW = Namespace('https://ekgf.org/ontology/raw/')
