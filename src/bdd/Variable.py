from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from bdd.Definition import Definition
from bdd.bdd import Base


class Variable(Definition):
    __tablename__ = None

    __mapper_args__ = {
        'polymorphic_identity': 'variable'
    }

    # True if it's the first time a variable is used.
    first_definition = Column(Boolean, default=False)
