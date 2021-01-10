from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import ast
from src.bdd.bdd import Base
from src.bdd.Variable import Variable
from src.bdd.Function import Function
from src.bdd.Class import Class


class Type(Base):
    __tablename__ = 'type'

    id = Column(Integer, primary_key=True)

    name = Column(String(50))
    variable = relationship("Variable", back_populate="type")
    function = relationship("Function", back_populates="type")
    classes = relationship("Class", back_populates="type")


def get_type_assign(module_ast, scope = None):
    """ Return type of the variable set by module_ast which is a
        ast.Assign instance"""
    if type(module_ast) == ast.Assign:
        module_ast = module_ast.value
    # Unary operator
    if type(module_ast) == ast.UnaryOp:
        return get_type_assign(module_ast.operand)
    # Binary operator
    elif type(module_ast) == ast.BinOp:
        tl = get_type_assign(module_ast.left)
        tr = get_type_assign(module_ast.right)
        for type_right in tr:
            if type_right in tl:
                pass
            else:
                test_sub = False
                for type_left in tl:
                    if issubclass(type_right, type_left):
                        test_sub = True
                if not test_sub:
                    tl.append(type_right)
        return tl
    # Name
    elif type(module_ast, scope) == ast.Name:
        var_id = module_ast.id
        if scope.exist(var_id):
            for sc in scope.get_parents():
                for var in sc.variable:
                    if var.name == var_id:
                        return var.type
        return [None]
    # Function call
    elif type(module_ast) == ast.Call:
        pass
    # Constant
    elif type(module_ast) == ast.Constant:
        return [type(module_ast.value)]
    return 0


def get_type_func_return(module_ast):
    pass
