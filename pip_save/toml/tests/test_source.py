from unittest import TestCase

from pip_save.toml.regex import BASIC_STRING
from pip_save.toml.source import Source, ExpectationError


class TestSource(TestCase):
    # EOF
    def test_expect_eof_true(self):
        text = ''
        s = Source(text)
        # not raises InvalidTomlError
        s.expect_eof()

    def test_expect_eof_false(self):
        text = '121'
        s = Source(text)
        with self.assertRaises(ExpectationError):
            s.expect_eof()

    # any text chunk
    def test_expect_any_text_chunk_true(self):
        text = 'Hello'
        s = Source(text)
        # not raises anything
        s.expect(text)

    def test_expect_any_text_chunk_false(self):
        text = 'World'
        s = Source(text)
        with self.assertRaises(ExpectationError):
            s.expect('Hello')

    # regex
    def test_expect_string_regex_true(self):
        text = '"Hello"'
        s = Source(text)
        s.expect_regex(BASIC_STRING)