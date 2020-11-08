from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.bdd.bdd import Base
from src.bdd.Variable import Variable
from src.bdd.Function import Function
from src.bdd.Class import Class


class Scope(Base):
    __tablename__ = 'scope'

    id = Column(Integer, primary_key=True)

    indent_level = Column(Integer)
    indent_level_id = Column(Integer)

    # To access module, class or function scope
    name = Column(String(50))

    module_id = Column(Integer, ForeignKey("module.id"))
    module = relationship("Module", back_populates="scope")
    variable = relationship("Variable", back_populates="scope", cascade="all, delete, delete-orphan")
    function = relationship("Function", back_populates="scope", cascade="all, delete, delete-orphan")
    classes = relationship("Class", back_populates="scope", cascade="all, delete, delete-orphan")

    def exist(self, variable_name):
        """Return True if variable already exists in scope."""
        for scope in self.module.scope:
            if scope <= self:
                for variable in scope.variable:
                    if variable.name == variable_name:
                        return True
        return False

    def __lt__(self, other):
        return self.indent_level < other.indent_level

    def __eq__(self, other):
        return self.indent_level == other.indent_level and self.indent_level_id == other.indent_level_id

    def __le__(self, other):
        return self < other or self == other
