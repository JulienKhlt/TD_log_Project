import builtins
import copy
import logging
import pathlib
import re
from urllib.parse import urlparse

import numpy
from pygls.types import (CompletionItem, CompletionItemKind, CompletionList,
                         CompletionParams, Position, CompletionTriggerKind)
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

def make_variable_completion_item(word):
    """Return a LSP::CompletionItem for variable name WORD."""
    return CompletionItem(word, CompletionItemKind.Variable)

def make_class_completion_item(word, add_args=True):
    """Return a LSP::CompletionItem for class name WORD."""
    if add_args:
        return CompletionItem(word, CompletionItemKind.Class, insert_text=f"{word}()")
    else:
        return CompletionItem(word, CompletionItemKind.Class)

def make_function_completion_item(word, add_args=True):
    """Return a LSP::CompletionItem for function name WORD."""
    if add_args:
        return CompletionItem(word, CompletionItemKind.Function, insert_text=f"{word}()")
    else:
        return CompletionItem(word, CompletionItemKind.Class)

def make_import_completion_item(word):
    """Return a LSP::CompletionItem for function name WORD."""

    return CompletionItem(word, CompletionItemKind.Module)

def make_external_completion_item(word):
    """Return a LSP::CompletionItem for function name WORD."""

    return CompletionItem(word, CompletionItemKind.Module)

def make_builtin_completion_item(word):
    return CompletionItem(word, CompletionItemKind.Function)

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
    """A class that adds some useful methods to CompletionParams. -> Binds LS and RS together!"""

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

    # Errors can be made!
    MAX_DISTANCE = 1

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
        return self.context.triggerKind == CompletionTriggerKind.TriggerCharacter

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

        if self.is_dot_completion():
            self.completion_types.append(CompletionType.DOT_COMPLETION)

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

    def complete_semantic_variable(self):
        """Return a list of CompletionItem for variable completion."""
        real_lineno = self.position.line + 1
        variable_list = self.module.complete_variable(self.get_word(), real_lineno)
        return [make_variable_completion_item(var_name) for var_name in variable_list]

    def complete_semantic_class(self):
        """Return a list of CompletionItem for class completion."""
        real_lineno = self.position.line + 1
        class_list = self.module.complete_class(self.get_word(), real_lineno)
        return [make_class_completion_item(var_name) for var_name in class_list]

    def complete_semantic_function(self):
        """Return a list of CompletionItem for function completion."""
        real_lineno = self.position.line + 1
        function_list = self.module.complete_function(self.get_word(), real_lineno)
        return [make_function_completion_item(var_name) for var_name in function_list]

    def complete_semantic_external(self):
        """Return a list of CompletionItem for external external completion."""
        module_list = self.module.complete_external(self.get_word())
        return [make_external_completion_item(module_name) for module_name in module_list]

    def complete_semantic_builtins(self):
        """Return a list of matching builtins definition."""
        builtins_list = []
        regex = re.compile(rf'^{self.get_word()}')

        for builtin in dir(builtins):
            if regex.match(builtin):
                builtins_list.append(make_builtin_completion_item(builtin))

        return builtins_list


    def complete_semantic(self):
        """Return a list of CompletionItem for semantic completion."""
        completion_list = []

        # TODO : You can do better!
        completion_list += self.complete_semantic_variable()
        completion_list += self.complete_semantic_class()
        completion_list += self.complete_semantic_function()
        completion_list += self.complete_semantic_external()
        completion_list += self.complete_semantic_builtins()

        return completion_list

    def complete_heritage(self):
        """Retun a list of CompletionItem for heritage completion. (.i.e semantic completion with class name)"""
        real_lineno = self.position.line + 1
        class_list = self.module.complete_class(self.get_word(), real_lineno)
        return [make_class_completion_item(var_name, False) for var_name in class_list]

    def complete_import(self):
        """Return a list of CompletionItem for import completion (i.e. module pathes)"""
        paths = self.server_context.project.complete_import(self.get_word())
        return [make_import_completion_item(path) for path in paths]

    def complete_import_from(self):
        """Return a list of CompletionItem for import/from completion (i.e. definition in module)"""

        # TODO: might take a while, better work on smthing else!
        return []

    def complete(self):
        """Return CompletionList for given context."""
        completion_item_list = []
        completion_types = self.get_completion_types()

        if CompletionType.KEYWORD_COMPLETION in completion_types:
            completion_item_list += self.complete_keyword()
        if CompletionType.SEMANTIC_COMPLETION in completion_types:
            completion_item_list += self.complete_semantic()
        if CompletionType.HERITAGE_COMPLETION in completion_types:
            completion_item_list += self.complete_heritage()
        if CompletionType.IMPORT_COMPLETION in completion_types:
            completion_item_list += self.complete_import()
        if CompletionType.IMPORT_FROM_COMPLETION in completion_types:
            completion_item_list += self.complete_import_from()
        if CompletionType.DOT_COMPLETION in completion_types:
            logging.error("NOT IMPLEMENTED!")

        return CompletionList(False, completion_item_list)
