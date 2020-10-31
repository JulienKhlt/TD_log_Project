from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from bdd.bdd import Base


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)

    name = Column(String(50))
    path = Column(String(200))

    active = Column(Boolean)

    config = relationship("Config", uselist=False, back_populates="project")
    modules = relationship("Module", back_populates="project")
