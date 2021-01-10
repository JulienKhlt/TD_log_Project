from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.bdd.Definition import Definition
from src.bdd.bdd import Base


class Variable(Definition):
    __tablename__ = 'variable'

    __mapper_args__ = {
        'polymorphic_identity': 'variable'
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = relationship("Type", back_populates="variable")
    scope = relationship("Scope", back_populates="variable")
    # True if it's the first time a variable is used.
    first_definition = Column(Boolean, default=False)
