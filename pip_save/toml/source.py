from typing import Match
from typing import Pattern, Optional
from typing import Union


class InvalidTomlError(RuntimeError):
    pass


class ExpectationError(InvalidTomlError):
    pass


class Source(object):
    def __init__(self, text: str) -> None:
        self._text = text  # type: str
        self._last_consumed = None  # type: Optional[Union[Match, str]]

    @property
    def last_consumed(self) -> str:
        if not isinstance(self._last_consumed, str):
            # match
            return self._last_consumed.group('res')

        return self._last_consumed

    # EOF
    def consume_eof(self) -> bool:
        if not self._text:
            self._last_consumed = ''
            return True
        return False

    def expect_eof(self) -> None:
        is_eof_consumed = self.consume_eof()
        if not is_eof_consumed:
            raise ExpectationError('No EOF present.')

    # any text chunk
    def consume(self, text_chunk: str) -> bool:
        if not self._text.startswith(text_chunk):
            return False

        self._text = self._text[len(text_chunk):]
        self._last_consumed = text_chunk
        return True

    def expect(self, text_chunk: str) -> None:
        is_consumed = self.consume(text_chunk)
        if not is_consumed:
            raise ExpectationError('"{text}" does not contain match for string "{string}"'
                                   .format(text=self._text[:100],
                                           string=text_chunk))

    # regex
    def consume_regex(self, regex: Pattern) -> bool:
        match = regex.match(self._text)
        if not match:
            return False

        self._text = self._text[len(match.group('res')):]
        self._last_consumed = match
        return True

    def expect_regex(self, regex: Pattern) -> None:
        match = self.consume_regex(regex)
        if not match:
            raise ExpectationError('{text} does not contain match for regex {regex}'
                                   .format(text=self._text[:100],
                                           regex=regex))

    # check if next, but don't advance
    def seek(self, s: str) -> bool:
        return self._text.startswith(s)

    def seek_regex(self, rgx: Pattern) -> bool:
        match = rgx.match(self._text)
        return bool(match)

        # def record_current_state(self):
        #     self.backtrack_stack.append(self.text)
        #
        # def commit(self):
        #     # set last recorded state to the current position
        #     # remove last recording
        #     self.backtrack_stack.pop()
        #     # set new recording to current state
        #     self.record_current_state()
        #
        # def rollback(self):
        #     # set current state to the last recorded
        #     self.text = self.backtrack_stack.pop()
        #
        # @contextmanager
        # def record_previous_state(self):
        #     self.backtrack_stack.append(self.text)
        #     try:
        #         yield
        #     except ExpectationError:
        #         self.rollback()
        #     else:
        #         # remove last recorded state
        #         source.backtrack_stack.pop()
