import ast
import re
from pathlib import Path

from src.bdd.Class import Class
from src.bdd.Function import Function
from src.bdd.Import import Import
from src.bdd.ImportFrom import ImportFrom
from src.bdd.Scope import Scope
from src.bdd.Variable import Variable
from src.bdd.Type import get_type_assign, Type, get_type_func_return


def calculate(module):
    """Populate module with its scopes, variables, functions and classes."""

    module_path = Path(module.path)
    module_name = module.name

    if module_path.is_dir():
        module_path = module_path.joinpath('__init__.py')

    with open(str(module_path), 'r') as file:
        module_text = file.read()
    module_ast = ast.parse(module_text, module_name)

    module_scope = Scope(indent_level=0, indent_level_id=0, name=module_name, lineno=0)
    module.scope.append(module_scope)

    indent_table = {0: 0}

    calculate_rec(module, module_scope, module_ast, indent_table)
    # print(ast.dump(module_ast))


def handle_assign_node(scope, single_target, module_ast):
    if type(single_target) == ast.Name:
        var = Variable(name=single_target.id, scope=scope, lineno=single_target.lineno, colno=single_target.col_offset)
        if not scope.exist(single_target.id):
            var.first_definition = True
        type_list = get_type_assign(module_ast)
        for _type_ in type_list:
            cls_type = Type(name=str(_type_))
            var.type.append(cls_type)
        scope.variable.append(var)


COND_STMT = [ast.If, ast.For, ast.AsyncFor, ast.While]


def handle_cond_stmt(scope, cond_node, indent_table):
    indent_level, indent_level_id = indent(scope.indent_level, indent_table)
    new_scope = Scope(indent_level=indent_level, indent_level_id=indent_level_id, lineno=cond_node.lineno)
    new_scope.parent = scope
    scope.module.scope.append(new_scope)

    if type(cond_node) == ast.For or type(cond_node) == ast.AsyncFor:
        handle_assign_node(new_scope, cond_node.target, None)

    for stmt in cond_node.body:
        calculate_rec(scope.module, new_scope, stmt, indent_table)

    # TODO Check if code isn't duplicated
    indent_level, indent_level_id = indent(scope.indent_level, indent_table)
    new_scope = Scope(indent_level=indent_level, indent_level_id=indent_level_id, lineno=cond_node.lineno)
    new_scope.parent = scope
    scope.module.scope.append(new_scope)

    for stmt in cond_node.orelse:
        calculate_rec(scope.module, new_scope, stmt, indent_table)


def handle_fun_def(scope, def_node, indent_table):
    indent_level, indent_level_id = indent(scope.indent_level, indent_table)
    new_scope = Scope(indent_level=indent_level, indent_level_id=indent_level_id, name=def_node.name,
                      lineno=def_node.lineno)
    new_scope.parent = scope
    new_scope.func_def = def_node.name
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
    new_scope = Scope(indent_level=indent_level, indent_level_id=indent_level_id, name=class_node.name,
                      lineno=class_node.lineno)
    new_scope.parent = scope
    scope.module.scope.append(new_scope)

    scope.classes.append(Class(name=class_node.name))
    scope.variable.append(Variable(name=class_node.name))

    # Later we will have a special function to parse function_node (to handle type return for example)
    for stmt in class_node.body:
        calculate_rec(scope.module, new_scope, stmt, indent_table)


def handle_import(scope, import_node):
    for alias in import_node.names:
        scope.module.imports.append(Import(name=alias.name, asname=alias.asname))


def handle_import_from(scope, import_node):
    if not import_node.module:
        import_node.module = scope.module.path
    else:
        import_node.module = '/'.join(import_node.module.split('.'))
    for alias in import_node.names:
        scope.module.imports_from.append(ImportFrom(name=import_node.module,
                                                    target_name=alias.name, target_asname=alias.asname))


def handle_return(module_ast, current_scope):
    # return type
    ret_type = get_type_assign(module_ast.value)
    # add return type to function
    func_name = current_scope.func_def
    parents = current_scope.get_parents()[1:]
    for parent in parents:
        if parent.function:
            for func in parent.function:
                if func_name == func.name:
                    func.return_type.append(Type(name=str(ret_type)))


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
                handle_assign_node(current_scope, target, module_ast)
        else:
            handle_assign_node(current_scope, module_ast.targets, module_ast)
    elif type(module_ast) in COND_STMT:
        handle_cond_stmt(current_scope, module_ast, indent_table)
    elif type(module_ast) == ast.FunctionDef:
        handle_fun_def(current_scope, module_ast, indent_table)
    elif type(module_ast) == ast.ClassDef:
        handle_class_def(current_scope, module_ast, indent_table)
    elif type(module_ast) == ast.Import:
        handle_import(current_scope, module_ast)
    elif type(module_ast) == ast.ImportFrom:
        handle_import_from(current_scope, module_ast)
    elif type(module_ast) == ast.Return:
        handle_return(module_ast, current_scope)
    else:
        # print(f"Unrecognized node: {type(module_ast)}")
        pass


def get_relative_path(from_path, fullpath):
    match = re.search(from_path, fullpath)
    if match:
        return fullpath[match.end() + 1:]
