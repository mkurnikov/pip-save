from unittest import TestCase

from pip_save.toml.writer import format_keyword


class TestFormatValue(TestCase):
    def assertFormatted(self, val: str, dest_text: str):
        formatted = format_keyword(val)
        self.assertEqual(formatted, dest_text)

    def test_empty_keyword(self):
        self.assertFormatted('', '""')

    def test_simple_keyword(self):
        self.assertFormatted('hello', 'hello')

    def test_complex_keyword(self):
        self.assertFormatted('hello world', '"hello world"')
