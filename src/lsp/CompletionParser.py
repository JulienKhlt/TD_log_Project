import builtins
import copy
from src.lsp.Logger import logging
import pathlib
import re
from urllib.parse import urlparse

import numpy
from pygls.types import (CompletionItem, CompletionItemKind, CompletionList,
                         CompletionParams, Position, CompletionTriggerKind)
from pygls.workspace import (RE_START_WORD, position_from_utf16,
                             position_to_utf16)
from src.rs.CompletionRequest import CompletionRequest
from src.rs.CompletionTypes import CompletionType

RE_WORD_BEFORE = re.compile(r"(([A-Za-z_0-9]|\.)*\(?)$")

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

class CompletionParser(CompletionParams):
    """A class that adds some useful methods to CompletionParams. -> Binds LS and RS together!"""

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
        self._module = None

    @property
    def module(self):
        if self._module:
            return self._module

        module = self.server_context.project.get_module(self.get_document_path())
        if not module:
            logging.error(f"Module at {self.get_document_path()} is not registered!")

        self._module = module
        return self._module

    @property
    def rs_object(self):
        """Return RS Object from given context."""
        if not self.need_context_computation():
            logging.info(f"Stay within module {self.module.name} context.")
            return self.module

        return self.get_context()


    def get_document_path(self):
        """Return Path from Uri."""
        return pathlib.Path(urlparse(self.get_document().uri).path)

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
            word_before_match = RE_WORD_BEFORE.findall(substart)[0]

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

    def need_context_computation(self):
        """I need those type inference PL!!!"""

        # We check that symbols preceding the completion is smthing like foo.bar.
        if re.match('.*\..*', self.get_word_before()):
            return True


        return False

    def get_completion_types(self):
        """Return a map of CompletionType that is computed with given context."""

        # We should use an enum...
        if self.completion_types:
            return self.completion_types

        self.completion_types = {}
        if self.is_heritage_completion():
            self.completion_types[CompletionType.HERITAGE_COMPLETION] = True

        if self.is_import_completion():
            self.completion_types[CompletionType.IMPORT_COMPLETION] = True

        if self.is_import_from_completion():
            self.completion_types[CompletionType.IMPORT_FROM_COMPLETION] = True

        if not self.completion_types:
            self.completion_types[CompletionType.SEMANTIC_COMPLETION] = True
            self.completion_types[CompletionType.SNIPPET_COMPLETION] = True
            self.completion_types[CompletionType.BUILTINS_COMPLETION] = True
            self.completion_types[CompletionType.KEYWORD_COMPLETION] = True

        if self.need_context_computation():
            self.completion_types[CompletionType.KEYWORD_COMPLETION] = False
            self.completion_types[CompletionType.BUILTINS_COMPLETION] = False

        return self.completion_types

    @property
    def lineno(self):
        return self.position.line + 1

    def split_completion_object(self, completion_object):
        """Return a list of string reprenting the object that should be looked for consecutively.
        For example: foo.bar -> ["foo", "bar"]."""
        object_symbol_list = completion_object.split('.')
        if object_symbol_list[-1] == '':
            object_symbol_list.pop()

        return object_symbol_list

    def get_context(self):
        """Return context for given symbol in given context. Context can be a Type or a Module."""
        symbol_chain = self.split_completion_object(self.get_word_before())
        current_rs_object = self.module

        for symbol in symbol_chain:
            try:
                current_rs_object = current_rs_object.get_object(symbol)
                logging.info(f"New context found: {current_rs_object.name}")
            except:
                logging.error(f"{type(current_rs_object)} has no method get_object yet.")
                return current_rs_object

        return current_rs_object

    def complete_dot(self):
        """Check type of word before (Object or Module ?) and give completions accordingly."""

        symbol_chain = self.split_completion_object(self.get_word_before())

        if len(symbol_chain) > 2:
            logging.error("Can't complete complex chain object yet!")
            return []
        else:
            new_context = self.get_context(self.module, symbol_chain[0])
            if not new_context:
                logging.error(f"Can't complete without valid context. {symbol_chain[0]} doesn't point to a valid object in {self.module.name} context.")
                return []

            new_context.complete
            logging.info("Context found!")

    def complete(self):
        """Return CompletionList for given context."""

        completion_request = CompletionRequest(self.rs_object, self.get_word(), self.lineno, self.get_completion_types())
        return completion_request.complete()
