from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from bdd.bdd import Base


class Variable(Base):
    __tablename__ = 'variable'

    id = Column(Integer, primary_key=True)

    name = Column(String(50))

    scope_id = Column(Integer, ForeignKey("scope.id"))
    scope = relationship("Scope")

    # True if it's the first time a variable is used.
    first_definition = Column(Boolean, default=False)

    lineno = Column(Integer)
    colno = Column(Integer)