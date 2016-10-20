from unittest import TestCase

from pip_save.metadata.dependencies import VersionedDependency
from pip_save.metadata.project import Project
from pip_save.toml.model import Root


class TestDependencyManagement(TestCase):
    def test_add_dependency(self):
        root = Root()
        project = Project(root)
        dep = VersionedDependency('django', '==1.10.2')
        project.add_dependency(dep)

        self.assertTrue(dep in project.deps)
        self.assertTrue('django' in root.nodes['deps'])
        self.assertTrue(('deps', 'django') in root.statement_nodes)

