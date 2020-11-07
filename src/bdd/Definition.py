from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.bdd.bdd import Base


class Definition(Base):
    # We use Single Table Inheritance, might change for Joint Heritage if too much difference appears
    
    __tablename__ = 'definition'

    id = Column(Integer, primary_key=True)

    name = Column(String(50))

    scope_id = Column(Integer, ForeignKey("scope.id"))
    scope = relationship("Scope")

    lineno = Column(Integer)
    colno = Column(Integer)

    definition_type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'definition',
        'polymorphic_on': definition_type
    }
