from collections import namedtuple
from typing import Any, Union
from typing import List
from typing import Tuple

from pip_save.toml.model import Root, NotSupported, Table
from pip_save.toml.model import TomlStatementNodes
from pip_save.toml.parser import parse_statement, KVEntry, Comment, ParsedTable
from pip_save.toml.regex import ENCLOSING_WHITESPACE_CHARS
from pip_save.toml.source import Source


def parse_statements(text: str) -> List[Any]:
    source = Source(text)
    statements = []
    while len(source._text) > 0:
        source.consume_regex(ENCLOSING_WHITESPACE_CHARS)
        # source.consume_regex(TILL_NEW_LINE_REGEX)
        # is_consumed = source.consume('\n')
        # if is_consumed:
        #     statements.append(NewLine())

        statement = parse_statement(source)
        # source.consume_regex(TILL_NEW_LINE_REGEX)
        # #
        # is_consumed = source.consume('\n')
        # if is_consumed:
        #     statements.append(NewLine())
        source.consume_regex(ENCLOSING_WHITESPACE_CHARS)

        statements.append(statement)

    source.expect_eof()
    return statements


UnmergedTable = namedtuple('UnmergedTable', ['name', 'content'])


def merge_tables(tables: List[UnmergedTable]) -> Root:
    sorted_tables = sorted(tables, key=lambda table: len(table.name))

    root = Root()
    for name, content in sorted_tables:
        if name == ():
            root = content
            continue

        internal_table = root
        for part in name[:-1]:
            if part not in internal_table:
                internal_table[part] = Table(parent=internal_table,
                                             parent_table_ref_key=part)

            internal_table = internal_table[part]

        content.parent = internal_table
        content.parent_table_ref_key = name[-1]
        internal_table.nodes[name[-1]] = content

    return root


def parse_toml(text: Union[str, bytes]) -> Root:
    if isinstance(text, bytes):
        text = text.decode()

    text = text.replace('\r\n', '\n')
    statements = parse_statements(text)

    tables = [UnmergedTable((), Root())]  # type: List[UnmergedTable]
    current_table = tables[0].content

    # statement_nodes = list()  # type: List[Tuple[str, ...]]
    statement_nodes = TomlStatementNodes()
    current_table_name = ()  # type: Tuple[str, ...]
    comment_counter = 1  # type: int
    newline_counter = 1  # type: int

    for statement in statements:
        if isinstance(statement, KVEntry):
            absolute_key_name = current_table_name + (statement.key,)
            if absolute_key_name in statement_nodes:
                raise NotSupported('Key overwrite is not permitted.')
            statement_nodes[absolute_key_name] = statement.val

            current_table.nodes[statement.key] = statement.val

        if isinstance(statement, Comment):
            comment_name = '#' + str(comment_counter)
            comment_counter += 1
            absolute_comment_name = current_table_name + (comment_name,)
            statement_nodes[absolute_comment_name] = statement.text

            current_table.nodes[comment_name] = statement.text
        #
        # if isinstance(statement, NewLine):
        #     newline_name = '%' + str(newline_counter)
        #     newline_counter += 1
        #     absolute_newline_name = current_table_name + (newline_name,)
        #     statement_nodes[absolute_newline_name] = NewLine()
        #
        #     current_table.nodes[newline_name] = NewLine()

        if isinstance(statement, ParsedTable):
            if statement.name in statement_nodes:
                raise NotSupported('Table overwrite is not permitted.')
            statement_nodes[statement.name] = Table()

            new_table = Table()
            tables.append(UnmergedTable(statement.name, new_table))
            current_table = new_table

            current_table_name = statement.name

    root = merge_tables(tables)
    root.set_statement_nodes(statement_nodes)
    return root
