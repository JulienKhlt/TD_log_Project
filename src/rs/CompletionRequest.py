import logging
import builtins
import re
from src.rs.PythonKeywords import KEYWORDS
from src.rs.CompletionTypes import CompletionType
from pygls.types import (CompletionItem, CompletionItemKind, CompletionList,
                         CompletionParams, Position, CompletionTriggerKind)

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

class CompletionRequest:
    """Wrapper that take RS Object and compute LS Completion Response."""
    def __init__(self, rs_object, symbol_to_complete, lineno, completion_types):
        self.rs_object = rs_object
        self.symbol_to_complete = symbol_to_complete
        self.completion_types = completion_types
        self.lineno = lineno

    def complete(self):
        """Return CompletionList for given context."""
        completion_item_list = []

        if self.rs_object is not None:
            if self.completion_types.get(CompletionType.KEYWORD_COMPLETION, False):
                completion_item_list += self.complete_keyword()
            if self.completion_types.get(CompletionType.SEMANTIC_COMPLETION, False):
                completion_item_list += self.complete_semantic()
            if self.completion_types.get(CompletionType.HERITAGE_COMPLETION, False):
                completion_item_list += self.complete_heritage()
            if self.completion_types.get(CompletionType.IMPORT_COMPLETION, False):
                completion_item_list += self.complete_import()
            if self.completion_types.get(CompletionType.IMPORT_FROM_COMPLETION, False):
                completion_item_list += self.complete_import_from()
            if self.completion_types.get(CompletionType.BUILTINS_COMPLETION, False):
                completion_item_list += self.complete_semantic_builtins()
            # if CompletionType.DOT_COMPLETION in completion_types:
            # self.complete_dot()
        else:
            logging.error("Invalid context, can't complete.")

        return CompletionList(False, completion_item_list)

    def complete_keyword(self):
        """Return a list of CompletionItem for keyword completion."""

        word = self.symbol_to_complete
        completion_item_list = []
        for keyword in KEYWORDS:
            if re.match(rf"^{word}", keyword):
                completion_item_list.append(make_keyword_completion_item(keyword))

        return completion_item_list

    def complete_semantic_variable(self):
        """Return a list of CompletionItem for variable completion."""
        variable_list = self.rs_object.complete_variable(self.symbol_to_complete, self.lineno)
        return [make_variable_completion_item(var_name) for var_name in variable_list]

    def complete_semantic_class(self):
        """Return a list of CompletionItem for class completion."""
        class_list = self.rs_object.complete_class(self.symbol_to_complete, self.lineno)
        return [make_class_completion_item(var_name) for var_name in class_list]

    def complete_semantic_function(self):
        """Return a list of CompletionItem for function completion."""
        function_list = self.rs_object.complete_function(self.symbol_to_complete, self.lineno)
        return [make_function_completion_item(var_name) for var_name in function_list]

    def complete_semantic_external(self):
        """Return a list of CompletionItem for external external completion."""
        module_list = self.rs_object.complete_external(self.symbol_to_complete)
        return [make_external_completion_item(module_name) for module_name in module_list]

    def complete_semantic_builtins(self):
        """Return a list of matching builtins definition."""
        builtins_list = []
        regex = re.compile(rf'^{self.symbol_to_complete}')

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
        # completion_list += self.complete_semantic_builtins()

        return completion_list

    def complete_heritage(self):
        """Retun a list of CompletionItem for heritage completion. (.i.e semantic completion with class name)"""
        class_list = self.rs_object.complete_class(self.symbol_to_complete, self.lineno)
        return [make_class_completion_item(var_name, False) for var_name in class_list]

    def complete_import(self):
        """Return a list of CompletionItem for import completion (i.e. module pathes)"""
        paths = self.rs_object.project.complete_import(self.symbol_to_complete)
        return [make_import_completion_item(path) for path in paths]

    def complete_import_from(self):
        """Return a list of CompletionItem for import/from completion (i.e. definition in module)"""

        # TODO: might take a while, better work on smthing else!
        return []
