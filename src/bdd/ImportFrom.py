from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.bdd.bdd import Base


class ImportFrom(Base):
    __tablename__ = 'import_from'

    id = Column(Integer, primary_key=True)

    name = Column(String(200), default="")

    module_from_id = Column(Integer, ForeignKey("module.id"))
    module_from = relationship("Module", foreign_keys=module_from_id)

    module_to_id = Column(Integer, ForeignKey("module.id"))
    module_to = relationship("Module", foreign_keys=module_to_id)

    target_name = Column(String(50), default="")
    target_asname = Column(String(50))

    target_id = Column(Integer, ForeignKey("definition.id"))
    target = relationship("Definition")

