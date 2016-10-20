import re
from collections import OrderedDict
from collections import namedtuple
from typing import Pattern, Union, List, Tuple

from pip_save.toml.regex import MULTILINE_BASIC_STRING_REGEX, BASIC_STRING, NUMBER_REGEX, LITERAL_STRING, \
    NEWLINE_ESCAPE_CHARS_REGEX, SHORT_UNICODE_REGEX, LONG_UNICODE_REGEX, ESCAPE_CHARS_REGEX, ESCAPES_MAPPING, \
    LITERAL_MULTILINE_STRING, ENCLOSING_WHITESPACE_CHARS, KEYWORD_REGEX, WHITESPACE_REGEX, COMMENT_REGEX
from pip_save.toml.source import Source, InvalidTomlError, ExpectationError


class DoesNotMatch(InvalidTomlError):
    pass


class InlineTable(OrderedDict):
    pass


ValueType = Union[float, int, str, bool, list, InlineTable]


def _parse_regex(s: Source, regex: Pattern) -> str:
    match = s.consume_regex(regex)
    if not match:
        raise DoesNotMatch('Cannot match {text}... to regex {regex}'.format(
            text=s._text[:100],
            regex=regex
        ))

    return s.last_consumed


def _parse_string(source: Source, string_regex=BASIC_STRING, separator='"') -> str:
    source.expect(separator)
    res = []
    while True:
        if not source.consume_regex(string_regex):
            raise DoesNotMatch('Invalid string starting from {text}'
                               .format(text=source._text[:100]))
        res.append(source.last_consumed)

        # start of some escape character
        if not source.consume('\\'):
            break
        # do nothing if new line chars encountered
        # corresponds to \
        if source.consume_regex(NEWLINE_ESCAPE_CHARS_REGEX):
            pass

        # read unicode characters
        elif source.consume_regex(SHORT_UNICODE_REGEX) or source.consume_regex(LONG_UNICODE_REGEX):
            res.append(chr(int(source.last_consumed, 16)))

        else:
            # fail if no escape character follows
            source.expect_regex(ESCAPE_CHARS_REGEX)
            res.append(ESCAPES_MAPPING[source.last_consumed])

    source.expect(separator)
    return ''.join(res)


def _parse_basic_string(source: Source) -> str:
    return _parse_string(source, string_regex=BASIC_STRING,
                         separator='"')


def _parse_multiline_string(source: Source) -> str:
    return _parse_string(source, string_regex=MULTILINE_BASIC_STRING_REGEX,
                         separator='"""')


def _parse_number(parsed_str: str) -> Union[int, float]:
    parsed_str = parsed_str.replace('_', '')
    if '.' in parsed_str or 'e' in parsed_str or 'E' in parsed_str:
        return float(parsed_str)
    else:
        return int(parsed_str, 10)


def _parse_literal_string(source: Source, string_regex=LITERAL_STRING, separator='\'') -> str:
    source.expect(separator)

    is_matched = source.consume_regex(string_regex)
    if not is_matched:
        raise DoesNotMatch()

    parsed_str = source.last_consumed
    source.expect(separator)

    return parsed_str


def _parse_basic_literal_string(source: Source) -> str:
    return _parse_literal_string(source, string_regex=LITERAL_STRING,
                                 separator='\'')


def _parse_multiline_literal_string(source: Source) -> str:
    return _parse_literal_string(source, string_regex=LITERAL_MULTILINE_STRING,
                                 separator='\'\'\'')


# def expect_enclosing_whitespace_chars(source: Source):
#     source.expect_regex(ENCLOSING_WHITESPACE_CHARS)


class MixedTypesArray(InvalidTomlError):
    pass


def _parse_array(source: Source) -> List[ValueType]:
    array_type = None  # type: type
    items = []  # type: List[ValueType]
    source.expect('[')

    try:
        while True:
            source.consume_regex(ENCLOSING_WHITESPACE_CHARS)
            parsed_val = parse_value(source)

            if array_type is not None and \
                    not isinstance(parsed_val, array_type):
                raise MixedTypesArray

            if array_type is None:
                array_type = type(parsed_val)

            items.append(parsed_val)

            source.consume_regex(ENCLOSING_WHITESPACE_CHARS)
            source.expect(',')
    except (ExpectationError, DoesNotMatch):
        pass

    source.consume_regex(ENCLOSING_WHITESPACE_CHARS)
    source.expect(']')
    return items


def _parse_inline_table(source: Source) -> InlineTable:
    table = InlineTable()
    source.expect('{')
    if not source.consume('}'):
        source.consume_regex(WHITESPACE_REGEX)
        kv_entry = parse_kv_entry(source)

        if source.last_consumed == '}':
            raise InvalidTomlError('Cannot have nested inline tables.')

        table[kv_entry.key] = kv_entry.val

        while source.consume(','):
            source.consume_regex(WHITESPACE_REGEX)
            kv_entry = parse_kv_entry(source)
            table[kv_entry.key] = kv_entry.val
            source.consume_regex(WHITESPACE_REGEX)

        source.expect('}')

    return table


def parse_value(source: Source) -> ValueType:
    boolean_match = source.consume_regex(re.compile(r'(?P<res>(true)|(false))'))
    if boolean_match:
        return source.last_consumed == 'true'

    if source.seek('"""'):
        return _parse_multiline_string(source)

    if source.seek('"'):
        return _parse_basic_string(source)

    if source.seek('\'\'\''):
        return _parse_multiline_literal_string(source)

    if source.seek('\''):
        return _parse_literal_string(source)

    # datetime_match = source.consume_regex(DATETIME_REGEX)
    # if datetime_match:
    #     return _parse_datetime(source.last_consumed)

    number_match = source.consume_regex(NUMBER_REGEX)
    if number_match:
        return _parse_number(source.last_consumed)

    if source.seek('['):
        return _parse_array(source)

    if source.seek('{'):
        return _parse_inline_table(source)

    raise DoesNotMatch('Cannot find valid TOML value in string {text}'
                       .format(text=source._text[:100]))


KVEntry = namedtuple('KVEntry', ['key', 'val'])
ParsedTable = namedtuple('ParsedTable', ['name'])
Comment = namedtuple('Comment', ['text'])


def parse_keyword(source: Source) -> str:
    if source.seek('"'):
        return _parse_basic_string(source)

    if source.seek('\''):
        return _parse_literal_string(source)

    match = source.consume_regex(KEYWORD_REGEX)
    if not match:
        raise DoesNotMatch()

    return source.last_consumed


def parse_kv_entry(source: Source) -> KVEntry:
    key = parse_keyword(source)

    source.consume_regex(WHITESPACE_REGEX)
    source.expect('=')
    source.consume_regex(WHITESPACE_REGEX)

    val = parse_value(source)
    return KVEntry(key, val)


def _parse_table_name(source: Source) -> Tuple[str, ...]:
    source.consume_regex(WHITESPACE_REGEX)
    keys = [parse_keyword(source)]
    source.consume_regex(WHITESPACE_REGEX)

    while source.consume('.'):
        source.consume_regex(WHITESPACE_REGEX)
        key = parse_keyword(source)
        keys.append(key)
        source.consume_regex(WHITESPACE_REGEX)

    return tuple(keys)


def parse_table(source: Source) -> ParsedTable:
    source.expect('[')
    keys = _parse_table_name(source)
    source.expect(']')

    return ParsedTable(keys)


def parse_line_comment(source: Source) -> Comment:
    source.expect('#')
    source.consume_regex(COMMENT_REGEX)
    text = source.last_consumed

    source.expect_regex(re.compile(r'(?P<res>\n|\Z)'))
    return Comment(text)


StatementType = Union[KVEntry, ParsedTable, Comment]


def parse_statement(source: Source) -> StatementType:
    if source.seek('#'):
        return parse_line_comment(source)

    if source.seek('['):
        return parse_table(source)

    kv_entry = parse_kv_entry(source)
    return kv_entry
