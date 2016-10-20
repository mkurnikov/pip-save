import re

# internal content of a basic string (within quotes):
# no ", no control characters (\000 - \037), no \ (in regex has to be escaped, hence two \\)
# MY_BASIC_STRING = re.compile(r'"(?P<res>[^"\000-\037]|\\[bnrtf"\'\\/]*)"')

BASIC_STRING = re.compile(r'(?P<res>[^"\\\000-\037]*)')

# internal content of multiline string:
# \n == \012 is allowed
# at most two consecutive "
# MY_MULTILINE_BASIC_STRING_REGEX = re.compile(r'"{3}(?P<res>("{0,2}[^"\000-\011\013-\037])*)"{3}')
MULTILINE_BASIC_STRING_REGEX = re.compile(r'(?P<res>("{0,2}[^"\\\000-\011\013-\037])*)')

# literal strings = raw strings in python. no escaping allowed
# no ", no control characters (\000 - \037)
LITERAL_STRING = re.compile(r"(?P<res>[^'\000-\037]*)")

# internal content of multiline literal string:
# \n == \012 is allowed
# at most two consecutive '
LITERAL_MULTILINE_STRING = re.compile(r"(?P<res>(?:'{0,2}[^'\000-\011\013-\037])*)")

# like python variable name, but can start with number
KEYWORD_REGEX = re.compile(r'(?P<res>[0-9a-zA-Z\-_]+)')

# number (float or integer)
# BASE.DECIMALe+-EXP
NUMBER_REGEX = re.compile(r'(?P<res>[+-]?'  # sign (? - zero or one)
                          r'(?:0|[1-9](?:_?\d)*)'  # part before the dot
                          r'(?:\.\d(?:_?\d)*)?'  # after the dot
                          r'(?:[eE][+-]?(?:\d(?:_?\d)*))?)')  # exponent

NEWLINE_ESCAPE_CHARS_REGEX = re.compile('(?P<res>\n[ \t\n]*)')

SHORT_UNICODE_REGEX = re.compile(r'u(?P<res>([0-9a-fA-F]{4}))')  # \u0001
LONG_UNICODE_REGEX = re.compile(r'U(?P<res>([0-9a-fA-F]{8}))')  # \U00010001
ESCAPE_CHARS_REGEX = re.compile(r'(?P<res>[bnrt"\'\\/f])')

ESCAPES_MAPPING = {'b': '\b', 'n': '\n', 'r': '\r', 't': '\t', '"': '"', '\'': '\'',
                   '\\': '\\', '/': '/', 'f': '\f'}

# DATETIME_REGEX = re.compile(r'(?P<res>' + rfc3339_regex.pattern + ')')

ENCLOSING_WHITESPACE_CHARS = re.compile(r'(?P<res>([ \t]|\n)*)')
WHITESPACE_REGEX = re.compile(r'(?P<res>([ \t])*)')
# KEYWORD_REGEX = re.compile(r'[0-9a-zA-Z-_]+')
# ENCLOSING_WHITESPACE_CHARS = re.compile(r'(?P<res>[ \t]|\n)*') # space or tab OR just \n

COMMENT_REGEX = re.compile(r'(?P<res>([^\n]*))(?:\n|\Z)')
