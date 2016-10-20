from unittest import TestCase

from pip_save.toml.assemble import parse_toml
from pip_save.toml.writer import to_toml


class TestWrite(TestCase):
    def assertRenderedTheSame(self, text):
        stripped_text = text.strip()
        root = parse_toml(stripped_text)

        rendered_toml = to_toml(root)
        stripped_rendered_toml = rendered_toml.strip()
        self.assertEqual(stripped_rendered_toml, stripped_text)

    def test_empty_file(self):
        text = """"""
        self.assertRenderedTheSame(text)

    def test_comment(self):
        text = """
# hello
        """
        self.assertRenderedTheSame(text)

    def test_root_keywords(self):
        text = """
a = 1
b = 2
        """
        self.assertRenderedTheSame(text)

    def test_empty_table(self):
        text = """
[table]
        """
        self.assertRenderedTheSame(text)

    def test_two_tables(self):
        text = """
[table]

[table2]
        """
        self.assertRenderedTheSame(text)

    def test_table_with_keywords(self):
        text = """
[table]
a = 1
b = 2
        """
        self.assertRenderedTheSame(text)

    def test_table_and_comments(self):
        text = """
# hello
[table]
a = 1
b = 2
        """
        self.assertRenderedTheSame(text)

    def test_table_and_inline_table(self):
        text = """
# hello
[table]
a = {version = "1.10.1", name = "django"}
b = 2
        """
        self.assertRenderedTheSame(text)

    def test_big_complex_toml(self):
        text = """
name = "doc"
version = 1
[deps]
django = "1.10.2"

[dev_deps]
# dev dependencies
pytest = "4.0.1"
array = [1, 2]
        """
        self.assertRenderedTheSame(text)

    def test_two_comments(self):
        text = """
[deps]
# hello
# everybody
        """
        self.assertRenderedTheSame(text)

    def test_nested_tables(self):
        text = """
[table.nested]
key = "value"

[table]
key2 = 11

[table.nested.twice]
pair = "shoes"
        """
        self.assertRenderedTheSame(text)

#     def test_newlines(self):
#         text = """
# [deps]
#
# # hello
# [dev_deps]
#
#
# [extras]
#         """
#         self.assertRenderedTheSame(text)