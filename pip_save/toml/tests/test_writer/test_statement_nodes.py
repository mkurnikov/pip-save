from collections import OrderedDict
from unittest import TestCase

from pip_save.toml.model import TomlStatementNodes, Table


class TestStatementNodes(TestCase):
    def test_append(self):
        toml_nodes = TomlStatementNodes()
        toml_nodes[('keyword',)] = '1'

        self.assertEqual(len(toml_nodes), 1)
        self.assertTrue(('keyword',) in toml_nodes)

    def test_insert_after(self):
        od = OrderedDict()
        od[('deps',)] = Table()
        od[('django',)] = '1.10.2'

        toml_nodes = TomlStatementNodes(od)
        toml_nodes.insert_after(('deps',), ('flask',), '1.3')
        self.assertEqual(toml_nodes.keys(), [('deps',), ('flask',), ('django',)])

    def test_insert_before(self):
        od = OrderedDict()
        od[('deps',)] = Table()
        od[('django',)] = '1.10.2'

        toml_nodes = TomlStatementNodes(od)
        toml_nodes.insert_before(('django',), ('flask',), '1.3')
        self.assertEqual(toml_nodes.keys(), [('deps',), ('flask',), ('django',)])

