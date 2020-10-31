from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from bdd.bdd import Base


class Class(Base):
    __tablename__ = 'class'

    id = Column(Integer, primary_key=True)

    name = Column(String(50))

    scope_id = Column(Integer, ForeignKey("scope.id"))
    scope = relationship("Scope")

