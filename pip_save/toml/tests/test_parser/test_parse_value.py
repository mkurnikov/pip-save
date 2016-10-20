from pip_save.toml.parser import InlineTable
from pip_save.toml.tests.test_parser._base import ParseValueTestCase


class TestParseValue(ParseValueTestCase):
    # basic string
    def test_parse_basic_string(self):
        self.assertValueParsedCorrectly('"hello"', 'hello')

    def test_parse_empty_string(self):
        self.assertValueParsedCorrectly('""', '')

    def test_no_newlines_allowed(self):
        self.assertInvalidToml('"hello\n"')

    def test_escape_sequences(self):
        self.assertValueParsedCorrectly(r'"hello\\world\n"', 'hello\\world\n')

    def test_escapes_only_string(self):
        self.assertValueParsedCorrectly(r'"\n\t"', '\n\t')

    # multiline string
    def test_multiline_string(self):
        self.assertValueParsedCorrectly('"""hello"""', 'hello')

    def test_multiline_string_few_lines(self):
        self.assertValueParsedCorrectly('"""hello\n\nworld"""', 'hello\n\nworld')

    def test_ml_string_allowes_quotes(self):
        self.assertValueParsedCorrectly('"""hello""world"""', 'hello""world')

    def test_ml_string_backslashes_alone_disappear_and_remove_all_whitespaces(self):
        self.assertValueParsedCorrectly('"""hello \\\n world"""', 'hello world')

    def test_ml_escape_sequences(self):
        self.assertValueParsedCorrectly(r'"""hello\\world\n"""', 'hello\\world\n')

    # literals
    def test_literals(self):
        self.assertValueParsedCorrectly(r"'C:\Users\nodejs\templates'", r"C:\Users\nodejs\templates")

    def test_quotes_in_literal(self):
        self.assertValueParsedCorrectly(r"'Tom \"Dubs\" Preston-Werner'", r'Tom \"Dubs\" Preston-Werner')

    # # multiline literals
    def test_multiline_literals(self):
        self.assertValueParsedCorrectly(r"'''C:\Users\nodejs\templates'''", r"C:\Users\nodejs\templates")

    def test_quotes_in_multiline_literal(self):
        self.assertValueParsedCorrectly(r"'''Tom \"Dubs\" Preston-Werner'''", r'Tom \"Dubs\" Preston-Werner')

    # numbers
    def test_number(self):
        self.assertValueParsedCorrectly('11', 11)

    def test_underscored_number(self):
        self.assertValueParsedCorrectly('1_100_100', 1100100)

    def test_big_exponent(self):
        self.assertValueParsedCorrectly('-1.213_233e-10', -1.213233e-10)

    # boolean
    def test_parse_true(self):
        self.assertValueParsedCorrectly('true', True)

    def test_parse_false(self):
        self.assertValueParsedCorrectly('false', False)

    def test_parse_similar_string(self):
        self.assertValueParsedCorrectly('"false"', 'false')


class TestParseArray(ParseValueTestCase):
    # array
    def test_empty_array(self):
        self.assertValueParsedCorrectly('[]', [])

    def test_empty_array_whitespace_inside(self):
        self.assertValueParsedCorrectly('[ \t]', [])

    def test_integer(self):
        self.assertValueParsedCorrectly('[1]', [1])

    def test_integer_array(self):
        self.assertValueParsedCorrectly('[1, 2]', [1, 2])

    def test_integer_array_newlines(self):
        self.assertValueParsedCorrectly('[1, \n2]', [1, 2])

    def test_integer_array_trailing_comma(self):
        self.assertValueParsedCorrectly('[1, 2,]', [1, 2])

    def test_mixed_array_is_forbidden(self):
        self.assertInvalidToml('[1, "2"]')

    def test_whitespaces_everywhere(self):
        self.assertValueParsedCorrectly('[1, 2,    3,\n\n ]', [1, 2, 3])

    def test_array_of_arrays(self):
        self.assertValueParsedCorrectly('[[1, 2], ["1", "2"]]', [[1, 2], ['1', '2']])

    def test_two_commas(self):
        self.assertInvalidToml('[1,,]')

    def test_two_number_split(self):
        self.assertInvalidToml('[1 2]')


class TestParseInlineTable(ParseValueTestCase):
    def test_empty_table(self):
        self.assertValueParsedCorrectly('{}', InlineTable())

    def test_invalid_toml_entry(self):
        self.assertInvalidToml('{hello = world}')

    def test_simple_entry(self):
        self.assertValueParsedCorrectly('{hello = "world"}', InlineTable(**{'hello': 'world'}))

    def test_trailing_comma_is_disallowed(self):
        self.assertInvalidToml('{hello = "world",}')

    def test_nested_inline_tables_are_disallowed(self):
        self.assertInvalidToml('{hello = {hello2 = 2}, entry = 3}')

    def test_parse_inline_table_preserves_order(self):
        self.assertValueParsedCorrectly('{one = 1, two = 2, three = 3}',
                                        InlineTable([('one', 1), ('two', 2), ('three', 3)]))
