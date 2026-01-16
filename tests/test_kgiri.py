from rdflib import URIRef

import ekg_lib
from ekg_lib.kgiri import EKG_NS, set_kgiri_base


class TestKGIRI:
    def test_kgiri(self):
        set_kgiri_base(URIRef('https://abc.def.ghi'))
        actual = EKG_NS['KGIRI'].term('xx')
        expected = URIRef('https://abc.def.ghi/id/xx')
        assert expected == actual


class TestParseIdentityKey:
    def test_1(self):
        actual = ekg_lib.parse_identity_key('commercialRegisterNumber')
        assert 'commercial-register-number' == actual

    def test_2(self):
        actual = ekg_lib.parse_identity_key('employeeId')
        assert 'employee-id' == actual

    def test_3(self):
        actual = ekg_lib.parse_identity_key(
            'Ich möchte die Qualität des Produkts überprüfen, bevor ich es kaufe.'
        )
        assert (
            'ich-moechte-die-qualitaet-des-produkts-ueberpruefen-bevor-ich-es-kaufe'
            == actual
        )

    def test_4(self):
        actual = ekg_lib.parse_identity_key('#(this) & {that};')
        assert 'this-and-that' == actual

    def test_5(self):
        actual = ekg_lib.parse_identity_key('theFATCA&someOtherDoddFrank')
        assert 'the-fatca-and-some-other-dodd-frank' == actual
