from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from bdd.bdd import Base


class Import(Base):
    __tablename__ = 'import'

    id = Column(Integer, primary_key=True)

    name = Column(String(200))
    asname = Column(String(50))

    module_from_id = Column(Integer, ForeignKey("module.id"))
    module_from = relationship("Module", foreign_keys=module_from_id)

    module_to_id = Column(Integer, ForeignKey("module.id"))
    module_to = relationship("Module", foreign_keys=module_to_id)

