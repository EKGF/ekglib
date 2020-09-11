from ekglib.kgiri.various import parse_identity_key


class TestKgiriVarious:

    def test_parse_identity_key_lowercase_no_change(self):
        assert "foobar" == parse_identity_key("foobar")

    def test_parse_identity_key_some_uppercase_becomes_kebabcase_lowercase(self):
        assert "foo-bar" == parse_identity_key("fooBar")

    def test_parse_identity_key_all_uppercase_becomes_lowercase(self):
        assert "foobar" == parse_identity_key("FOOBAR")
