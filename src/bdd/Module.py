import ast
import datetime
import logging
from pathlib import Path

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from src.bdd.bdd import Base
from src.bdd.Scope import Scope
from src.parser.tools import *


class Module(Base):
    __tablename__ = "module"

    id = Column(Integer, primary_key=True)

    name = Column(String(50))
    path = Column(String(200))

    external = Column(Boolean, default=False)
    visit_date = Column(DateTime, default=datetime.datetime.now())

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="module")
    scope = relationship(
        "Scope", back_populates="module", cascade="all, delete, delete-orphan"
    )
    imports = relationship(
        "Import",
        back_populates="module_from",
        foreign_keys="Import.module_from_id",
        cascade="all, delete, delete-orphan",
    )

    imports_from = relationship(
        "ImportFrom",
        back_populates="module_from",
        foreign_keys="ImportFrom.module_from_id",
        cascade="all, delete, delete-orphan",
    )

    imports_to = relationship(
        "Import",
        back_populates="module_to",
        foreign_keys="Import.module_to_id",
        cascade="all",
    )

    imports_from_to = relationship(
        "ImportFrom",
        back_populates="module_to",
        foreign_keys="ImportFrom.module_to_id",
        cascade="all",
    )

    def update(self, source=None):
        self.scope = []
        self.imports = []
        self.imports_from = []

        self.visit_date = datetime.datetime.now()

        # We rebuild everything! (We don't really know how the module was changed...)
        # and tracking difference would be way less efficient (AST substraction)
        # We could really optimize with how the LS Protocol works, but it would require much more
        # work. (LSP tells us what changed in a file, we could theorically update the Module from here
        # instead of recomputing it entirely on change in the buffer. But it should be alright if file isn't
        # too big.)
        if not source:
            self.build()
        else:
            self.build_from_string(source)

    def get_imports_name(self):
        """Return name of imported modules in module."""
        imports_name = []
        for module_import in self.imports + self.imports_from:
            imports_name.append(module_import.name)
        return imports_name

    def build(self):
        """Index all scopes and imports within module."""

        module_path = Path(self.path)
        module_name = self.name

        if module_path.is_dir():
            module_path = module_path.joinpath("__init__.py")


        with open(str(module_path), "r") as file:
            module_text = file.read()
        self.build_from_string(module_text, True)

    def build_from_string(self, source, from_file=False):
        """Index from given string instead of using saved file (for real time completion)."""
        if not self.external:
            if from_file:
                logging.info(f"building module {self.name} from file.")
            else:
                logging.info(f"building module {self.name} from buffer.")

        try:
            module_ast = ast.parse(source, self.name)

            module_scope = Scope(indent_level=0, indent_level_id=0, name=self.name, lineno=0)
            self.scope.append(module_scope)

            indent_table = {0: 0}

            self.build_helper(module_scope, module_ast, indent_table)
        except SyntaxError:
            logging.warn(
                f"Couldn't parse {self.name} (Invalid Syntax)"
            )
        except Exception as error:
            logging.error(str(error))

    def build_helper(self, current_scope, module_ast, indent_table):
        """Recursive method to help build module."""
        if type(module_ast) == ast.Module:
            for next_ast in module_ast.body:
                self.build_helper(current_scope, next_ast, indent_table)
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
        elif type(module_ast) == ast.ImportFrom:
            handle_import_from(current_scope, module_ast)
        else:
            pass

    def get_scope_from_lineno(self, lineno):
        """Return Scope from this Module matching given line number."""
        good_scope = self.scope[0]
        for scope in self.scope:
            if scope.lineno > good_scope.lineno and scope.lineno <= lineno:
                good_scope = scope

        return good_scope

    def complete_variable(self, to_complete, lineno):
        """Return a list of string that corresponds to possible variable completion for TO_COMPLETE at LINENO."""
        # DONE add scope aware completion...
        logging.info(f"Tring to complete {to_complete} in module {self.name}")

        possibility = []
        scope = self.get_scope_from_lineno(lineno)
        completion_scopes = scope.get_parents()


        for completion_scope in completion_scopes:
            # Variable completion
            for scope_variable in completion_scope.variable:

                # TODO : Use levensthein/damerau
                regex = "^" + to_complete
                match = re.match(regex, scope_variable.name)
                if match:
                    possibility.append(scope_variable.name)

        return possibility
