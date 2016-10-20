from unittest import TestCase

from pip_save.metadata.dependencies import parse_dependency, VersionedDependency, InvalidEnvironmentMarkers
from pip_save.toml.parser import InlineTable


class TestParseVersionedDependency(TestCase):
    def test_parse_simple_versioned_dependency(self):
        dep = parse_dependency('django', '==1.10.2')

        self.assertTrue(isinstance(dep, VersionedDependency))
        self.assertEqual(dep.pkg_name, 'django')
        self.assertEqual(dep.matcher.specifiers, '==1.10.2')

    def test_parse_inline_table_versioned_dependency(self):
        dep = parse_dependency('django', InlineTable([('version', '==1.10.2')]))

        self.assertTrue(isinstance(dep, VersionedDependency))
        self.assertTrue(dep.pkg_name, 'django')
        self.assertEqual(dep.matcher.specifiers, '==1.10.2')

    def test_parse_dep_with_markers(self):
        dep = parse_dependency('django', InlineTable([('version', '==1.10.2'),
                                                      ('markers', 'python_version >= "1.0"')]))
        self.assertEqual(dep.markers, 'python_version >= "1.0"')

    def test_fail_if_invalid_marker(self):
        with self.assertRaises(InvalidEnvironmentMarkers):
            dep = parse_dependency('django', InlineTable([('version', '==1.10.2'),
                                                          ('markers', 'python_version1 >= "1.0"')]))
