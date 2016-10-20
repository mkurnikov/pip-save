from io import StringIO
from typing import List, Tuple, Union

from pip_save.toml.model import Root, NotSupported, Table
from pip_save.toml.parser import ValueType, Comment, InlineTable
from pip_save.toml.regex import KEYWORD_REGEX


_escapes = {'\n': 'n', '\r': 'r', '\\': '\\', '\t': 't', '\b': 'b', '\f': 'f', '"': '"'}


def _escape_string(s: str) -> str:
    result = []

    for char in s:
        if char in _escapes.keys():
            result.append('\\' + _escapes[char])
            continue

        result.append(char)

    return '"{}"'.format(''.join(result))


def _format_list(lst: List[ValueType]) -> str:
    formatted_values = []
    array_type = None
    for val in lst:
        if array_type is not None and type(val) != array_type:
            raise NotSupported('Mixed types array.')

        formatted_values.append(format_value(val))
        array_type = type(val)

    return '[{list}]'.format(list=', '.join(formatted_values))


def _format_inline_table(tbl: InlineTable) -> str:
    res = []
    for key, val in tbl.items():
        if isinstance(val, InlineTable):
            raise NotSupported('Nested inline tables.')

        res.append(format_kv_entry(key, val))

    return '{' + ', '.join(res) + '}'


def format_value(val: ValueType) -> str:
    if isinstance(val, bool):
        return 'true' if val else 'false'

    if isinstance(val, (int, float)):
        return str(val)

    if isinstance(val, str):
        return _escape_string(val)

    if isinstance(val, list):
        return _format_list(val)

    if isinstance(val, InlineTable):
        return _format_inline_table(val)

    raise NotSupported('Serializing {} is not supported.'.format(type(val)))


def trace_node_val(name: Tuple[str, ...], root: Root) -> Union[ValueType, Table, Comment]:
    current_table = root.nodes
    val = None
    for part in name:
        val = current_table[part]
        if isinstance(val, Table):
            current_table = val

    return val


def format_keyword(key: str) -> str:
    match = KEYWORD_REGEX.match(key)
    if not match or match.group() != key:
        return '"{key}"'.format(key=key)

    return key


def format_table_name(name: Tuple[str, ...]) -> str:
    parts = []
    for part in name:
        parts.append(format_keyword(part))

    return '[' + '.'.join(parts) + ']'


def format_kv_entry(key: str, val: ValueType) -> str:
    return format_keyword(key) + ' = ' + format_value(val)


def to_toml(root: Root) -> str:
    output = StringIO()
    first_table = True
    for node_name, val in root.statement_nodes.items():
        # val = trace_node_val(node_name, root)
        if val is None:
            raise KeyError

        if isinstance(val, Table):
            if not first_table:
                output.write('\n')
            else:
                first_table = False

            output.write(format_table_name(node_name))

        elif node_name[-1].startswith('#'):  # comment
            output.write('#' + val)

        else:
            # keyword
            output.write(format_keyword(node_name[-1]))
            output.write(' = ')
            output.write(format_value(val))

        output.write('\n')

    result_toml = output.getvalue()
    output.close()
    return result_toml
