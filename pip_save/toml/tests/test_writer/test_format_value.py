from unittest import TestCase

from pip_save.toml.model import NotSupported
from pip_save.toml.parser import ValueType, InlineTable
from pip_save.toml.writer import format_value


class TestFormatValue(TestCase):
    def assertFormatted(self, val: ValueType, dest_text: str):
        formatted = format_value(val)
        self.assertEqual(formatted, dest_text)

    def assertNotSupported(self, val: ValueType):
        with self.assertRaises(NotSupported):
            format_value(val)

    def test_format_numbers(self):
        self.assertFormatted(1, '1')
        self.assertFormatted(1.21, '1.21')
        self.assertFormatted(-1.21e-10, '-1.21e-10')
        self.assertFormatted(-1.21E-10, '-1.21e-10')

    def test_format_boolean(self):
        self.assertFormatted(True, 'true')
        self.assertFormatted(False, 'false')

    def test_format_string(self):
        self.assertFormatted('maxim', '"maxim"')
        self.assertFormatted(r'C:\templates', r'"C:\\templates"')
        self.assertFormatted('\n\n', r'"\n\n"')

    def test_format_list(self):
        self.assertFormatted([], '[]')
        self.assertFormatted([1, 2], '[1, 2]')
        self.assertFormatted(['str'], '["str"]')

    def test_mixed_arrays_are_not_supported(self):
        self.assertNotSupported(['11', 22])

    def test_fail_on_unsupported_type(self):
        self.assertNotSupported(())

    def test_inline_table(self):
        self.assertFormatted(InlineTable([('a', 1), ('b', 2)]),
                             '{a = 1, b = 2}')