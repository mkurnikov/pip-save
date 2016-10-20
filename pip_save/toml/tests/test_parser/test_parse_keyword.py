from pip_save.toml.tests.test_parser._base import ParseKeywordTestCase


class TestParseKeyword(ParseKeywordTestCase):
    def test_simple_keyword(self):
        self.assertKeywordParsedCorrectly('hello', 'hello')

    def test_numbers_keyword(self):
        self.assertKeywordParsedCorrectly('1234ahaha', '1234ahaha')

    def test_empty_keyword_disallowed(self):
        self.assertInvalidToml('')

    def test_basic_string_keyword(self):
        self.assertKeywordParsedCorrectly('"hello"', 'hello')

    def test_empty_basic_string(self):
        self.assertKeywordParsedCorrectly('""', '')

    def test_literal_string_keyword(self):
        self.assertKeywordParsedCorrectly(r"'C:\templates'", r'C:\templates')

    def test_literal_empty_string(self):
        self.assertKeywordParsedCorrectly("''", '')

    def test_dots_are_forbidden(self):
        self.assertInvalidToml('ada.boost')
