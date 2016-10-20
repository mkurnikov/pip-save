from unittest import TestCase

from pip_save.toml.assemble import parse_toml
from pip_save.toml.model import Root, Table


class TestRoot(TestCase):
    def test_add_new_key_creates_new_statement_node(self):
        text = """
key = "value"
        """
        root = parse_toml(text.strip())
        root['key2'] = 'value2'

        self.assertTrue(('key2',) in root.statement_nodes)

    def test_change_new_key(self):
        text = """
key = "value"
        """
        root = parse_toml(text.strip())
        root['key'] = 'value2'

        self.assertTrue(('key',) in root.statement_nodes)
        self.assertEqual(root.statement_nodes[('key',)], 'value2')

    def test_remove_root_key(self):
        text = """
key = "value"
        """
        root = parse_toml(text.strip())  # type: Root
        del root['key']

        self.assertTrue(('key',) not in root.statement_nodes)

    def test_add_new_table(self):
        text = """
key = "value"
        """
        root = parse_toml(text.strip())
        root['table'] = Table()

        self.assertTrue(('table',) in root.statement_nodes)
        self.assertEqual(len(root.statement_nodes), 2)
        self.assertTrue(isinstance(root.statement_nodes[('table',)], Table))

    def test_add_new_nested_table(self):
        text = """
key = "value"
        """
        root = parse_toml(text.strip())
        root['table.nested'] = Table()

        self.assertEqual(len(root.statement_nodes), 2)
        self.assertTrue(isinstance(root.statement_nodes[('table', 'nested')], Table))

    def test_add_kv_entry_to_table(self):
        text = """
[table]
        """
        root = parse_toml(text.strip())
        root['table']['hello'] = 'world'

        self.assertEqual(root.statement_nodes[('table', 'hello')], 'world')

    def test_kv_entry_value_in_table(self):
        text = """
[table]
hello = "world"
        """
        root = parse_toml(text.strip())
        root['table']['hello'] = 'ohmy'

        self.assertEqual(root.statement_nodes[('table', 'hello')], 'ohmy')

    def test_cannot_add_keyword_if_table_itself_not_exists(self):
        text = """
[table.nested]
hello = "world"
        """
        root = parse_toml(text.strip())
        with self.assertRaises(KeyError):
            root['table']['hey'] = 'ohmy'
