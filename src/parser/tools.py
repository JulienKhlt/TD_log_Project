import ast

from bdd.Class import Class
from bdd.Function import Function
from bdd.Import import Import
from bdd.Scope import Scope
from bdd.Variable import Variable


def calculate(module):
    """Populate module with its scopes, variables, functions and classes."""

    module_path = module.path
    module_name = module.name

    with open(module_path, 'r') as file:
        module_text = file.read()
    module_ast = ast.parse(module_text, module_name)

    module_scope = Scope(indent_level=0, indent_level_id=0, name=module_name)
    module.scope.append(module_scope)

    indent_table = {0: 0}

    calculate_rec(module, module_scope, module_ast, indent_table)
    print(ast.dump(module_ast))

def handle_assign_node(scope, single_target):
    if type(single_target) == ast.Name:
        if not scope.exist(single_target.id):
            scope.variable.append(Variable(name=single_target.id, scope=scope))

COND_STMT = [ast.If, ast.For, ast.AsyncFor, ast.While]
def handle_cond_stmt(scope, cond_node, indent_table):
    indent_level, indent_level_id = indent(scope.indent_level, indent_table)
    new_scope = Scope(indent_level=indent_level, indent_level_id=indent_level_id)
    scope.module.scope.append(new_scope)

    if type(cond_node) == ast.For or type(cond_node) == ast.AsyncFor:
        handle_assign_node(new_scope, cond_node.target)

    for stmt in cond_node.body:
        calculate_rec(scope.module, new_scope, stmt, indent_table)

    indent_level, indent_level_id = indent(scope.indent_level, indent_table)
    new_scope = Scope(indent_level=indent_level, indent_level_id=indent_level_id)
    scope.module.scope.append(new_scope)

    for stmt in cond_node.orelse:
        calculate_rec(scope.module, new_scope, stmt, indent_table)

def handle_fun_def(scope, def_node, indent_table):
    indent_level, indent_level_id = indent(scope.indent_level, indent_table)
    new_scope = Scope(indent_level=indent_level, indent_level_id=indent_level_id, name=def_node.name)
    scope.module.scope.append(new_scope)

    scope.function.append(Function(name=def_node.name))
    scope.variable.append(Variable(name=def_node.name))

    # Add arguments as variable
    for arg in def_node.args.args:
        if not scope.exist(arg.arg):
            new_scope.variable.append(Variable(name=arg.arg))

    # Later we will have a special function to parse function_node (to handle type return for example)
    for stmt in def_node.body:
        calculate_rec(scope.module, new_scope, stmt, indent_table)

def handle_class_def(scope, class_node, indent_table):
    indent_level, indent_level_id = indent(scope.indent_level, indent_table)
    new_scope = Scope(indent_level=indent_level, indent_level_id=indent_level_id, name=class_node.name)
    scope.module.scope.append(new_scope)

    scope.classes.append(Class(name=class_node.name))
    scope.variable.append(Variable(name=class_node.name))

    # Later we will have a special function to parse function_node (to handle type return for example)
    for stmt in class_node.body:
        calculate_rec(scope.module, new_scope, stmt, indent_table)

def handle_import(scope, import_node):
    for alias in import_node.names:
        scope.module.imports.append(Import(name=alias.name, asname=alias.asname))
def indent(current_indent_level, indent_table):
    """Return new indent_level and indent_level_id as a tuple and update indent_table"""
    new_scope_indent_level = current_indent_level + 1
    new_scope_indent_level_id = indent_table.get(new_scope_indent_level, -1) + 1
    indent_table[new_scope_indent_level] = new_scope_indent_level_id

    return new_scope_indent_level, new_scope_indent_level_id


def calculate_rec(module, current_scope, module_ast, indent_table):
    if type(module_ast) == ast.Module:
        for next_ast in module_ast.body:
            calculate_rec(module, current_scope, next_ast, indent_table)
    elif type(module_ast) == ast.Assign:
        if type(module_ast.targets) == list:
            for target in module_ast.targets:
                handle_assign_node(current_scope, target)
        else:
            handle_assign_node(current_scope, module_ast.targets)
    elif type(module_ast) in COND_STMT:
        handle_cond_stmt(current_scope, module_ast, indent_table)
    elif type(module_ast) == ast.FunctionDef:
        handle_fun_def(current_scope, module_ast, indent_table)
    elif type(module_ast) == ast.ClassDef:
        handle_class_def(current_scope, module_ast, indent_table)
    elif type(module_ast) == ast.Import:
        handle_import(current_scope, module_ast)
    else:
        print(f"Unrecognized node: {type(module_ast)}")