from pip_save.toml.parser import KVEntry, ParsedTable, Comment
from pip_save.toml.tests.test_parser._base import ParseStatementTestCase


class TestParseKVEntry(ParseStatementTestCase):
    def test_parse_keyword_statement(self):
        self.assertStatementParsedCorrectly('hello = "world"', KVEntry('hello', 'world'))

    def test_parse_no_spaces(self):
        self.assertStatementParsedCorrectly('hello="world"', KVEntry('hello', 'world'))

    def test_parse_array(self):
        self.assertStatementParsedCorrectly('hello=[1, 2]', KVEntry('hello', [1, 2]))

    def test_parse_a_lot_of_whitespaces(self):
        self.assertStatementParsedCorrectly('hello=                  \t\t[1, 2]',
                                            KVEntry('hello', [1, 2]))


class TestParseTable(ParseStatementTestCase):
    def test_empty_name_is_disallowed(self):
        self.assertInvalidToml('[]')

    def test_simple_table(self):
        self.assertStatementParsedCorrectly('[table]', ParsedTable(('table',)))

    def test_table_dashed_underscored(self):
        self.assertStatementParsedCorrectly('[table-1_22]', ParsedTable(('table-1_22',)))

    def test_nested_table(self):
        self.assertStatementParsedCorrectly('[table.a.b]', ParsedTable(('table', 'a', 'b')))

    def test_dot_can_be_applied_if_in_quotes(self):
        self.assertStatementParsedCorrectly('[table."much.better"]', ParsedTable(('table', 'much.better')))

    def test_dot_can_be_applied_if_in_literal(self):
        self.assertStatementParsedCorrectly(r"[table.'C:\template']", ParsedTable(('table', r'C:\template')))

    def test_whitespaces(self):
        self.assertStatementParsedCorrectly('[d.e.f]', ParsedTable(('d', 'e', 'f')))

    def test_big_whitespaces(self):
        self.assertStatementParsedCorrectly('[  d   .   e  .\t\t f\t\t ]', ParsedTable(('d', 'e', 'f')))


class TestParseLineComments(ParseStatementTestCase):
    def test_parse_simple_comment(self):
        self.assertStatementParsedCorrectly('#hello', Comment('hello'))
