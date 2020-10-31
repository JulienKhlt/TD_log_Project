from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from bdd.bdd import Base


class Scope(Base):
    __tablename__ = 'scope'

    id = Column(Integer, primary_key=True)

    indent_level = Column(Integer)
    indent_level_id = Column(Integer)

    module_id = Column(Integer, ForeignKey("module.id"))
    module = relationship("Module", back_populates="scope")
    variables = relationship("Variable", back_populates="scope")

