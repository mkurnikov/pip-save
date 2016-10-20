from unittest import TestCase

from pip_save.toml.assemble import parse_toml
from pip_save.toml.model import Root, Table, NotSupported
from pip_save.toml.parser import InlineTable


class TestAssembleParsing(TestCase):
    def assertParsedCorrectly(self, text: str, root: Root):
        parsed_root = parse_toml(text.strip())
        self.assertEqual(parsed_root, root)

    def assertNotSupported(self, text: str):
        with self.assertRaises(NotSupported):
            parse_toml(text.strip())

    def test_empty_root(self):
        text = """"""
        self.assertParsedCorrectly(text, Root())

    def test_can_add_key_entry_to_root(self):
        text = """
one = 1
        """
        self.assertParsedCorrectly(text, Root(nodes={
            'one': 1
        }))

    def test_key_reassign_not_supported(self):
        text = """
one = 1
one = 2
        """
        self.assertNotSupported(text)

    def test_key_table_reassign_is_not_supported(self):
        text = """
one = 1

[one]
two = 2
        """
        self.assertNotSupported(text)

    def test_parse_table(self):
        text = """
[test]
three = 3
        """
        self.assertParsedCorrectly(text, Root(nodes={
            'test': Table(nodes={
                'three': 3
            })
        }))

    def test_two_nested_tables(self):
        text = """
[table.nested]
key = "value"

[table]
key2 = 11

[table.nested.twice]
pair = "shoes"
        """
        self.assertParsedCorrectly(text, Root(nodes={
            'table': Table(nodes={
                'nested': Table(nodes={
                    'key': 'value',
                    'twice': Table(nodes={
                        'pair': 'shoes'
                    })
                }),
                'key2': 11})
        }))

    def test_override_table_with_key_not_supported(self):
        text = """
[table.nested]
key = "value"

[table]
nested = 11
"""
        self.assertNotSupported(text)

    def test_parse_various_values(self):
        text = """
[table]
one = 1
two = 2.2
three = [1, 2]
four = {one = 1, 1 = 3}
        """
        self.assertParsedCorrectly(text, Root(nodes={
            'table': Table(nodes={
                'one': 1,
                'two': 2.2,
                'three': [1, 2],
                'four': InlineTable([('one', 1), ('1', 3)])
            })
        }))

    def test_commented_supported(self):
        text = """
#hello
[table]
key2 = 11
        """
        self.assertParsedCorrectly(text, Root(nodes={
            '#1': 'hello',
            'table': Table(nodes={
                'key2': 11
            })
        }))

# def test_newlines(self):
#         text = """
# key = 1
#
# key2 = 2
#         """
#         self.assertParsedCorrectly(text, Root(nodes={
#             'key1': 1,
#             '%1': NewLine(),
#             'key2': 2
#         }))
