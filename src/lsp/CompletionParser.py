import copy
import logging
import re

import numpy
from pygls.types import (CompletionItem, CompletionItemKind, CompletionList,
                         CompletionParams, Position)
from pygls.workspace import (RE_START_WORD, position_from_utf16,
                             position_to_utf16)

RE_WORD_BEFORE = re.compile(r"([A-Za-z_0-9]*\(?)$")

def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = numpy.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])

def make_keyword_completion_item(word):
    """Return a LSP::CompletionItem for reserved keyword WORD."""
    return CompletionItem(word, CompletionItemKind.Keyword)

class CompletionType:
    """An enumeration of different type of completion."""

    IMPORT_COMPLETION = 0
    DOT_COMPLETION = 1
    SEMANTIC_COMPLETION = 2
    IMPORT_FROM_COMPLETION = 3
    HERITAGE_COMPLETION = 4
    SNIPPET_COMPLETION = 5
    KEYWORD_COMPLETION = 6


class CompletionParser(CompletionParams):
    """A class that adds some useful methods to CompletionParams."""

    KEYWORDS = [
        "False",
        "await",
        "else",
        "import",
        "pass",
        "None",
        "break",
        "except",
        "in",
        "raise",
        "True",
        "class",
        "finally",
        "is",
        "return",
        "and",
        "continue",
        "for",
        "lambda",
        "try",
        "as",
        "def",
        "from",
        "nonlocal",
        "while",
        "assert",
        "del",
        "global",
        "not",
        "with",
        "async",
        "elif",
        "if",
        "or",
        "yield"
    ]

    MAX_DISTANCE = 5

    def __init__(self, completionParams, server_context):
        super().__init__(
            completionParams.textDocument,
            completionParams.position,
            completionParams.context,
        )
        self.server_context = server_context

        # We could compute those at the object's creation! (But what is done is done...)
        self.word_before = None
        self.word = None
        self.line = None
        self.document = None
        self.completion_types = None

    def get_current_line(self):
        """Return a string matching the line under cursor."""
        if self.line:
            return self.line

        lines = self.server_context.workspace.get_document(self.textDocument.uri).lines
        row, _ = position_from_utf16(lines, self.position)
        self.line = lines[row]

        return self.line

    def get_lines(self):
        return self.get_document().lines

    def get_document(self):
        if self.document:
            return self.document

        self.document = self.server_context.workspace.get_document(
            self.textDocument.uri
        )
        return self.document

    def get_word(self):
        """Return a string matching the word to complete."""
        if self.word:
            return self.word

        self.word = self.get_document().word_at_position(self.position)

        return self.word

    def get_word_before(self):
        """Return a string matching the word prefixing the completion, if no such word exists, return an empty string."""
        if self.word_before:
            return self.word_before

        lines = self.get_lines()
        row, col = position_from_utf16(lines, self.position)
        line = lines[row]
        start = line[:col]

        word_start_match = RE_START_WORD.search(start)

        if not word_start_match:
            self.word = ""
            self.word_before = ""
        else:
            substart = start[: word_start_match.start()].rstrip()
            word_before_match = RE_WORD_BEFORE.findall(substart)

            self.word = word_start_match[0]
            self.word_before = word_before_match[0]
        return self.word_before

    def is_heritage_completion(self):
        """Return True if context matches an heritage completion."""
        current_line = self.get_current_line()

        match = re.match(r"class", current_line)
        if match:
            word_before = self.get_word_before()
            if word_before[-1] == "(":
                return True
        return False

    def is_import_completion(self):
        """Return True if context matches an import completion."""
        current_line = self.get_current_line()

        # Seperate cases! More difficult than I thought
        match = re.match(r"(import)|(from)", current_line)
        if match:
            word_before = self.get_word_before()
            if word_before == "from" or word_before == "import":
                # Need to check for multiple imports! (TODO)
                return True

            return False

    def is_import_from_completion(self):
        """Return if context matches an import ... from (HERE) completion."""

        current_line = self.get_current_line()

        match = re.match(r"from .* import", current_line)
        if match and self.get_word() != "import":
            return True

        return False

    def is_dot_completion(self):
        """I need those type inference PL!!!"""

        # TODO! (I can write it, but not the completion.)
        return False

    def get_completion_types(self):
        """Return a list of CompletionType that is computed with given context."""

        # We should use an enum...
        if self.completion_types:
            return self.completion_types

        self.completion_types = []
        if self.is_heritage_completion():
            self.completion_types.append(CompletionType.HERITAGE_COMPLETION)

        if self.is_import_completion():
            self.completion_types.append(CompletionType.IMPORT_COMPLETION)

        if self.is_import_from_completion():
            self.completion_types.append(CompletionType.IMPORT_FROM_COMPLETION)

        if not self.completion_types:
            self.completion_types.append(CompletionType.SEMANTIC_COMPLETION)
            self.completion_types.append(CompletionType.SNIPPET_COMPLETION)
            self.completion_types.append(CompletionType.KEYWORD_COMPLETION)

        return self.completion_types

    def complete_keyword(self):
        """Return a list of CompletionItem for keyword completion."""

        word = self.get_word()
        completion_item_list = []
        for keyword in CompletionParser.KEYWORDS:
            if levenshtein(word, keyword) < CompletionParser.MAX_DISTANCE + len(keyword) - len(word):
                completion_item_list.append(make_keyword_completion_item(keyword))

        return completion_item_list

    def complete(self):
        """Return CompletionList for given context."""
        completion_item_list = []
        completion_types = self.get_completion_types()

        logging.info(completion_types)

        if CompletionType.KEYWORD_COMPLETION in completion_types:
            completion_item_list += self.complete_keyword()

        return CompletionList(False, completion_item_list)
