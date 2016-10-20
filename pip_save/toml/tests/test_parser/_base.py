from typing import Any
from unittest import TestCase

from pip_save.toml.source import Source, InvalidTomlError
from pip_save.toml.parser import parse_value, parse_statement, ValueType, parse_keyword


class ParseValueTestCase(TestCase):
    def assertInvalidToml(self, original_text: str):
        s = Source(original_text)
        with self.assertRaises(InvalidTomlError):
            parse_value(s)

    def assertValueParsedCorrectly(self, original_text: str, expected: ValueType):
        s = Source(original_text)
        parsed = parse_value(s)
        self.assertEqual(parsed, expected)
        self.assertEqual(len(s._text), 0)


class ParseStatementTestCase(TestCase):
    def assertInvalidToml(self, original_text: str):
        s = Source(original_text)
        with self.assertRaises(InvalidTomlError):
            parse_statement(s)

    def assertStatementParsedCorrectly(self, original_text: str, expected: Any):
        s = Source(original_text)
        parsed = parse_statement(s)
        self.assertEqual(parsed, expected)
        self.assertEqual(len(s._text), 0)


class ParseKeywordTestCase(TestCase):
    def assertKeywordParsedCorrectly(self, text: str, expected: str):
        s = Source(text)
        parsed = parse_keyword(s)
        self.assertEqual(parsed, expected)
        self.assertEqual(len(s._text), 0)

    def assertInvalidToml(self, text: str):
        s = Source(text)
        with self.assertRaises(InvalidTomlError):
            parse_keyword(s)
            # if parsed less than whole string, raise exception
            if len(s._text) != 0:
                raise InvalidTomlError
                # try:
                #     parse_keyword(s)
                # except InvalidTomlError:
                #     pass
